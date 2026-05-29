from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.reasoning import ReasoningRequest, ReasoningResponse
from app.schemas.report_version import ReportVersionResponse
from app.services.app_settings_service import AppSettingsService
from app.services.report_version_service import ReportVersionService

from app.reasoning.providers.gemini import GeminiProvider
from app.grounding.grounding_service import GroundingService
from app.services.citation_service import CitationFormattingService
from app.reasoning.parser import ReasoningResponseParser
from app.preprocessing.engine import PreprocessingEngine
from app.services.reasoning_service import ReasoningOrchestrationService
from app.services.evidence_cache_service import EvidenceCacheService
from app.services.pubmed_client import PubMedClient

router = APIRouter(prefix="/reasoning", tags=["Reasoning"])

@router.post("/generate", response_model=ReasoningResponse)
async def generate_reasoning(
    request: ReasoningRequest,
    db: AsyncSession = Depends(get_db)
):
    api_key_setting = await AppSettingsService.get_setting_value(db, "gemini_api_key")
    if not api_key_setting:
        raise HTTPException(status_code=422, detail="Gemini API key is not configured. Please set it in Settings.")

    grounding_enabled_setting = await AppSettingsService.get_setting_value(db, "grounding_enabled")

    provider = GeminiProvider(
        api_key=str(api_key_setting),
        generation_model="gemini-3.1-flash-lite",
        grounding_model="gemini-2.5-flash",
        grounding_enabled=bool(grounding_enabled_setting) if grounding_enabled_setting is not None else True
    )
    
    cache_service = EvidenceCacheService()
    grounding_service = GroundingService(provider=provider, cache_service=cache_service)
    citation_service = CitationFormattingService()
    parser = ReasoningResponseParser()
    preprocessing_engine = PreprocessingEngine()

    if request.case_id == "test_verify_key":
        try:
            await provider.complete("Respond with OK", system="You are a helpful assistant.")
            return ReasoningResponse(
                report_version_id="verify",
                case_id="test_verify_key",
                version_number=1,
                status="success",
                message="API Key verified successfully."
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"API Key verification failed: {str(e)}")

    try:
        ncbi_api_key = await AppSettingsService.get_setting_value(db, "ncbi_api_key")
    except Exception:
        ncbi_api_key = None
    pubmed_client = PubMedClient(api_key=ncbi_api_key if ncbi_api_key else None)

    reasoning_service = ReasoningOrchestrationService(
        provider=provider,
        grounding_service=grounding_service,
        citation_service=citation_service,
        parser=parser,
        preprocessing_engine=preprocessing_engine,
        pubmed_client=pubmed_client
    )

    try:
        report_version = await reasoning_service.generate_report(db=db, request=request)
        return ReasoningResponse(
            report_version_id=str(report_version.id),
            case_id=str(report_version.case_id),
            version_number=report_version.version_number,
            status="success",
            message="Reasoning completed successfully."
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always close the per-request PubMedClient so the underlying
        # httpx.AsyncClient connection pool is released cleanly.
        await pubmed_client.close()

@router.get("/cases/{case_id}/reports", response_model=List[ReportVersionResponse])
async def list_reports_for_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    reports = await ReportVersionService.list_report_versions_for_case(db, case_id)
    return reports

@router.get("/reports/{report_id}", response_model=ReportVersionResponse)
async def get_report_by_id(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    report = await ReportVersionService.get_report_version(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report version not found")
    return report
