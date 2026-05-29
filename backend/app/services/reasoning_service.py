import json
import logging
import re

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.reasoning import ReasoningRequest
from app.models.report_version import ReportVersion
from app.services.case_service import CaseService
from app.services.report_version_service import ReportVersionService
from app.reasoning.providers.base import BaseAIProvider
from app.grounding.grounding_service import GroundingService
from app.services.citation_service import CitationFormattingService
from app.reasoning.parser import ReasoningResponseParser
from app.preprocessing.engine import PreprocessingEngine
from app.reasoning.prompts import format_reasoning_prompt, SYSTEM_PROMPT
from app.services.citation_verification_service import CitationVerificationService
from app.services.pubmed_client import PubMedClient
from app.reasoning.certainty_validator import CertaintyValidator


class ReasoningOrchestrationService:
    """
    Reasoning Orchestration Service.

    Architectural Notes:
    The ReasoningOrchestrationService acts as the central coordinator (Facade) for the complex reasoning pipeline.
    
    Schema v2 Pipeline:
    1. Validation: Fail early if the case doesn't exist.
    2. Preprocessing: Run deterministic heuristics first to reduce LLM workload and token count.
    3. Context Gathering: Fetch historical reports to enable differential evolution.
    4. Prompt Formatting: Assemble all clinical data and context into a strict structured schema.
    5. AI Generation: Perform the core LLM call with SYSTEM_PROMPT, optionally with integrated grounding.
    6. Parsing: Convert raw LLM text into validated structured Python dicts (v2 schema).
    7. Citation Merging: Merge grounding citations into the structured citations array.
    8. Deduplication: Remove duplicate citations.
    9. Persistence: Save the structured report as an immutable ReportVersion.
    """

    def __init__(
        self,
        provider: BaseAIProvider,
        grounding_service: GroundingService,
        citation_service: CitationFormattingService,
        parser: ReasoningResponseParser,
        preprocessing_engine: PreprocessingEngine,
        pubmed_client: PubMedClient = None
    ):
        self.provider = provider
        self.grounding_service = grounding_service
        self.citation_service = citation_service
        self.parser = parser
        self.preprocessing_engine = preprocessing_engine
        self.pubmed_client = pubmed_client or PubMedClient()
        self.citation_verification_service = CitationVerificationService(provider, self.pubmed_client)
        self.certainty_validator = CertaintyValidator()

    async def generate_report(self, db: AsyncSession, request: ReasoningRequest) -> ReportVersion:
        # Step 1: Validate - Check that the case exists using CaseService.get_case()
        case = await CaseService.get_case(db, request.case_id)
        if not case:
            raise RuntimeError(f"Case with id {request.case_id} not found.")

        # Step 2: Preprocess - Call preprocessing_engine.run(lab_data, physical_exam, anamnesis)
        preprocessing_result = self.preprocessing_engine.run(
            lab_data=request.laboratory_data.model_dump(),
            physical_exam=request.physical_exam.model_dump(),
            anamnesis=request.anamnesis.model_dump()
        )
        preprocessing_summary = json.dumps(preprocessing_result.model_dump()) if hasattr(preprocessing_result, "model_dump") else str(preprocessing_result)

        # Step 3: Get context - Fetch the latest existing report version for differential evolution context
        latest_report = await ReportVersionService.get_latest_report_version(db, request.case_id)
        previous_differentials = ""
        if latest_report:
            diffs = latest_report.differentials if latest_report else []
            previous_differentials = json.dumps(diffs)

        # Step 4: Format prompt - Call format_reasoning_prompt()
        clinical_data = {
            "anamnesis": request.anamnesis.model_dump(),
            "physical_exam": request.physical_exam.model_dump(),
            "labs": request.laboratory_data.model_dump(),
            "morphology": request.morphological_data.model_dump()
        }
        
        prompt = format_reasoning_prompt(
            preprocessing_result=preprocessing_summary,
            clinical_data=clinical_data,
            follow_up_context=request.follow_up_context or "",
            previous_differentials=previous_differentials
        )

        # Step 5: AI call - ALWAYS use provider.complete() for raw reasoning without web grounding
        # IMPORTANT: Now passing SYSTEM_PROMPT to the provider
        try:
            ai_response_text = await self.provider.complete(
                prompt, system=SYSTEM_PROMPT
            )
            logger.info(f"[PIPELINE LOG] Raw AI Reasoning:\n{ai_response_text}")
        except Exception as e:
            raise RuntimeError(f"AI provider failed during reasoning generation: {str(e)}")

        # Step 6: Parse - Call parser.parse_reasoning_response()
        parsed_response = self.parser.parse_reasoning_response(ai_response_text)
        
        # Step 6.5: Apply Certainty Policy Layer
        parsed_response = self.certainty_validator.apply_certainty_policies(parsed_response)
        
        missing_info = parsed_response.get("missing_information", [])
        if missing_info:
            logger.info(f"[PIPELINE LOG] Missing Data Identified:\n{json.dumps(missing_info, indent=2)}")

        # Step 7 & 8: Verify and Inject Citations using the new Verification Pipeline
        all_citations = []
        id_to_key = {}

        def get_cit_key(cit, prefixed_id):
            key = cit.get("pmid") or cit.get("doi") or cit.get("canonical_url") or cit.get("url") or cit.get("title", "")
            if isinstance(key, str):
                key = key.lower()
            return key if key else prefixed_id

        # 7a. Process summary.overview
        summary = parsed_response.get("summary")
        if isinstance(summary, dict) and summary.get("overview"):
            try:
                new_overview, verified_citations = await self.citation_verification_service.inject_citations(
                    db, summary["overview"]
                )
                for cit in verified_citations:
                    old_id = cit["id"]
                    new_id = f"summary_{old_id}"
                    cit["id"] = new_id
                    new_overview = new_overview.replace(f"{{{{cite:{old_id}}}}}", f"{{{{cite:{new_id}}}}}")
                    id_to_key[new_id] = get_cit_key(cit, new_id)
                parsed_response["summary"]["overview"] = new_overview
                all_citations.extend(verified_citations)
            except Exception as e:
                logger.error(f"Citation injection for summary.overview failed, continuing: {e}")

        # 7b. Process differentials[:3].reasoning
        differentials = parsed_response.get("differentials", [])
        for i, diff in enumerate(differentials[:3]):
            if isinstance(diff, dict) and diff.get("reasoning"):
                try:
                    new_reasoning, verified_citations = await self.citation_verification_service.inject_citations(
                        db, diff["reasoning"]
                    )
                    for cit in verified_citations:
                        old_id = cit["id"]
                        new_id = f"diff{i}_{old_id}"
                        cit["id"] = new_id
                        new_reasoning = new_reasoning.replace(f"{{{{cite:{old_id}}}}}", f"{{{{cite:{new_id}}}}}")
                        id_to_key[new_id] = get_cit_key(cit, new_id)
                    diff["reasoning"] = new_reasoning
                    all_citations.extend(verified_citations)
                except Exception as e:
                    logger.error(f"Citation injection for differentials[{i}].reasoning failed, continuing: {e}")

        # 8. Deduplicate and Renumber Globally
        if all_citations:
            unique_citations = self.citation_service.deduplicate_citations(all_citations)
            
            key_to_new_id = {}
            for i, cit in enumerate(unique_citations):
                old_prefixed_id = cit["id"]
                new_id = f"c{i+1}"
                cit["id"] = new_id
                cit["vancouver_string"] = self.citation_service.format_vancouver(cit, i + 1)
                key = get_cit_key(cit, old_prefixed_id)
                key_to_new_id[key] = new_id

            full_mapping = {}
            for prefixed_id, key in id_to_key.items():
                if key in key_to_new_id:
                    full_mapping[prefixed_id] = key_to_new_id[key]

            def replacer(m):
                cid = m.group(1)
                return f"{{{{cite:{full_mapping.get(cid, cid)}}}}}"

            if isinstance(summary, dict) and summary.get("overview"):
                parsed_response["summary"]["overview"] = re.sub(r'\{\{cite:([^}]+)\}\}', replacer, parsed_response["summary"]["overview"])
                
            for i, diff in enumerate(differentials[:3]):
                if isinstance(diff, dict) and diff.get("reasoning"):
                    diff["reasoning"] = re.sub(r'\{\{cite:([^}]+)\}\}', replacer, diff["reasoning"])

            parsed_response["citations"] = unique_citations
        else:
            parsed_response["citations"] = []

        # Step 9: Final Language Rendering Pass
        try:
            from app.services.language_enhancement_service import LanguageEnhancementService
            enhancement_service = LanguageEnhancementService(self.provider, self.parser)
            parsed_response = await enhancement_service.enhance_report_language(parsed_response)
        except Exception as e:
            logger.error(f"Language enhancement rendering pass failed, continuing with original: {e}")

        # Step 10: Persist - Build report_data mapped to exact ReportVersion column names
        report_data = {
            "summary": parsed_response.get("summary", {"overview": "", "severity": "moderate"}),
            "supporting_findings": parsed_response.get("supporting_findings", []),
            "contradictory_findings": parsed_response.get("contradictory_findings", []),
            "differentials": parsed_response.get("differentials", []),
            "next_steps": parsed_response.get("next_steps", []),
            "missing_information": parsed_response.get("missing_information", []),
            "citations": parsed_response.get("citations", []),
            "preprocessing_summary": preprocessing_result.model_dump() if hasattr(preprocessing_result, "model_dump") else {},
            "ai_provider": self.provider.provider_name,
            "ai_model": self.provider.generation_model,
            "grounding_used": request.use_grounding,
        }

        report = await ReportVersionService.create_report_version(
            db=db,
            case_id=request.case_id,
            report_data=report_data
        )
        logger.info(f"Report version {report.version_number} saved for case {request.case_id}")

        # Step 11: Return
        return report
