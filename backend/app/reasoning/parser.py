import json
import logging
import re
import json_repair
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Allowed enum values for validation
_SEVERITY_VALUES = {"low", "moderate", "high", "critical"}
_STRENGTH_VALUES = {"weak", "moderate", "strong"}
_URGENCY_VALUES = {"routine", "urgent", "emergent"}
_STEP_CATEGORIES = {"diagnostic", "monitoring", "treatment", "referral", "follow_up"}
_MISSING_CATEGORIES = {"history", "labs", "medications", "imaging", "risk_factors", "family_history", "physical_exam"}
_SOURCE_TYPES = {"pubmed", "doi", "journal", "guideline", "web"}


class ReasoningResponseParser:
    """
    Parses and validates the structured JSON response from the AI provider.
    
    Schema v2: Expects a structured object with typed sections
    (summary, supporting_findings, contradictory_findings, differentials,
    next_steps, missing_information, citations).
    
    Handles malformed responses gracefully with normalization and fallbacks.
    """
    
    def parse_reasoning_response(self, raw_text: str) -> Dict[str, Any]:
        """
        Attempts to extract and parse a JSON block from the raw AI response text.
        Returns a structured dictionary matching the v2 schema, or a fallback.
        """
        try:
            # Strip markdown code fences if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                # Remove opening fence (```json or ```)
                cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
                cleaned = re.sub(r'\n?```\s*$', '', cleaned)

            # Extract JSON block from raw text (from first { to last })
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if not match:
                logger.warning("No JSON block found in the AI response.")
                return self._fallback_response(raw_text)
                
            json_str = match.group(0)
            parsed = json_repair.loads(json_str)
            
            if not isinstance(parsed, dict):
                raise ValueError("Parsed JSON is not a dictionary.")
            
            # Validate required top-level keys.
            # NOTE: 'citations' is intentionally excluded — the retrieval pipeline
            # always constructs citations programmatically, so the LLM is not
            # expected to emit them.
            required_keys = {"summary", "differentials"}
            if not required_keys.issubset(parsed.keys()):
                missing = required_keys - parsed.keys()
                logger.warning(f"Parsed JSON is missing required keys: {missing}")
                # Attempt to map from v1 schema keys
                parsed = self._migrate_v1_to_v2(parsed)
            elif "citations" not in parsed:
                # Run migration to ensure citations key exists (even if empty)
                parsed = self._migrate_v1_to_v2(parsed)

            # Normalize all sections
            parsed = self._normalize(parsed)

            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode JSON from AI response: {e}")
            return self._fallback_response(raw_text)
        except Exception as e:
            logger.warning(f"Unexpected error parsing AI response: {e}")
            return self._fallback_response(raw_text)

    def _migrate_v1_to_v2(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to map old v1 schema keys to new v2 schema when the LLM
        falls back to the old format.
        """
        result = dict(parsed)

        # clinical_summary → summary
        if "clinical_summary" in result and "summary" not in result:
            summary_text = result.pop("clinical_summary", "")
            result["summary"] = {"overview": str(summary_text), "severity": "moderate"}

        # differential_diagnoses → differentials
        if "differential_diagnoses" in result and "differentials" not in result:
            old_diffs = result.pop("differential_diagnoses", [])
            new_diffs = []
            for d in old_diffs:
                if isinstance(d, dict):
                    likelihood = d.get("likelihood", "Medium")
                    conf_map = {"High": 0.85, "Medium": 0.55, "Low": 0.25}
                    conf_val = conf_map.get(likelihood, 0.5)
                    new_diffs.append({
                        "diagnosis": d.get("name", "Unknown"),
                        "reasoning_confidence": conf_val,
                        "evidence_confidence": conf_val,
                        "reasoning": f"Likelihood assessed as {likelihood}.",
                        "supporting_evidence": d.get("supporting", []),
                        "contradictory_evidence": d.get("contradicting", []),
                    })
            result["differentials"] = new_diffs

        # suggested_next_steps → next_steps
        if "suggested_next_steps" in result and "next_steps" not in result:
            old_steps = result.pop("suggested_next_steps", [])
            new_steps = []
            for step in old_steps:
                if isinstance(step, str):
                    new_steps.append({
                        "title": step[:80],
                        "category": "diagnostic",
                        "rationale": step,
                        "urgency": "routine",
                        "expected_outcome": "",
                        "risks_of_delay": None,
                    })
            result["next_steps"] = new_steps

        # missing_information (strings → objects)
        if "missing_information" in result:
            old_missing = result["missing_information"]
            if old_missing and isinstance(old_missing[0], str):
                new_missing = []
                for item in old_missing:
                    new_missing.append({
                        "item": item[:80] if isinstance(item, str) else str(item),
                        "category": "labs",
                        "why_it_matters": item if isinstance(item, str) else str(item),
                        "impact_on_assessment": "",
                        "possible_implications": "",
                    })
                result["missing_information"] = new_missing

        # supporting_findings (dict → list)
        if "supporting_findings" in result and isinstance(result["supporting_findings"], dict):
            old_sf = result.pop("supporting_findings")
            new_sf = []
            for dx_name, findings in old_sf.items():
                if isinstance(findings, list):
                    for f in findings:
                        new_sf.append({
                            "finding": str(f),
                            "explanation": f"Supports {dx_name}",
                            "strength": "moderate",
                        })
            result["supporting_findings"] = new_sf

        # contradictory_findings (dict → list)
        cf_key = "contradictory_findings"
        if cf_key not in result and "contradicting_findings" in result:
            result[cf_key] = result.pop("contradicting_findings")
        if cf_key in result and isinstance(result[cf_key], dict):
            old_cf = result.pop(cf_key)
            new_cf = []
            for dx_name, findings in old_cf.items():
                if isinstance(findings, list):
                    for f in findings:
                        new_cf.append({
                            "finding": str(f),
                            "explanation": f"Contradicts {dx_name}",
                            "significance": "Requires further evaluation",
                        })
            result[cf_key] = new_cf

        # references_section / evidence_references → citations
        if "citations" not in result:
            citations = []
            refs = result.pop("evidence_references", [])
            for i, ref in enumerate(refs):
                if isinstance(ref, dict):
                    citations.append({
                        "id": f"c{i+1}",
                        "label": ref.get("citation_text", f"Source {i+1}")[:40],
                        "source_type": "web",
                        "url": ref.get("url", ""),
                        "title": ref.get("citation_text", ""),
                        "journal": None,
                        "year": None,
                        "authors": None,
                    })
            result.pop("references_section", None)
            result["citations"] = citations

        return result

    def _normalize(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Defensive normalization to enforce correct types and enum values.
        """
        # ── Summary ──────────────────────────────────────────────────
        summary = parsed.get("summary")
        if summary is None:
            parsed["summary"] = {"overview": "", "severity": "moderate"}
        elif isinstance(summary, str):
            parsed["summary"] = {"overview": summary, "severity": "moderate"}
        elif isinstance(summary, dict):
            if "severity" not in summary or summary["severity"] not in _SEVERITY_VALUES:
                summary["severity"] = "moderate"
            if "overview" not in summary:
                summary["overview"] = ""

        # ── Supporting Findings ──────────────────────────────────────
        sf = parsed.get("supporting_findings")
        if not isinstance(sf, list):
            parsed["supporting_findings"] = []
        else:
            for item in sf:
                if isinstance(item, dict):
                    if item.get("strength") not in _STRENGTH_VALUES:
                        item["strength"] = "moderate"

        # ── Contradictory Findings ───────────────────────────────────
        cf = parsed.get("contradictory_findings")
        if not isinstance(cf, list):
            parsed["contradictory_findings"] = []

        # ── Differentials ────────────────────────────────────────────
        diffs = parsed.get("differentials")
        if not isinstance(diffs, list):
            parsed["differentials"] = []
        else:
            for d in diffs:
                if isinstance(d, dict):
                    # Clamp confidence to 0-1
                    # Fallback mapping from old schema
                    if "confidence" in d and "reasoning_confidence" not in d:
                        d["reasoning_confidence"] = d["confidence"]
                        d["evidence_confidence"] = d["confidence"]
                    
                    try:
                        r_conf = float(d.get("reasoning_confidence", 0.5))
                        d["reasoning_confidence"] = max(0.0, min(1.0, r_conf))
                    except (TypeError, ValueError):
                        d["reasoning_confidence"] = 0.5
                        
                    try:
                        e_conf = float(d.get("evidence_confidence", 0.5))
                        d["evidence_confidence"] = max(0.0, min(1.0, e_conf))
                    except (TypeError, ValueError):
                        d["evidence_confidence"] = 0.5
                        
                    # ── New Certainty Fields ──
                    d["certainty_tier"] = str(d.get("certainty_tier", "possible"))
                    d["is_provisional"] = bool(d.get("is_provisional", False))
                    
                    # ── Legacy Confidence Mapping ──
                    if "confidence" not in d:
                        d["confidence"] = d["reasoning_confidence"]
                    
                    # Ensure evidence lists
                    if not isinstance(d.get("supporting_evidence"), list):
                        d["supporting_evidence"] = []
                    if not isinstance(d.get("contradictory_evidence"), list):
                        d["contradictory_evidence"] = []

        # ── Next Steps ───────────────────────────────────────────────
        ns = parsed.get("next_steps")
        if not isinstance(ns, list):
            parsed["next_steps"] = []
        else:
            for step in ns:
                if isinstance(step, dict):
                    if step.get("category") not in _STEP_CATEGORIES:
                        step["category"] = "diagnostic"
                    if step.get("urgency") not in _URGENCY_VALUES:
                        step["urgency"] = "routine"

        # ── Missing Information ──────────────────────────────────────
        mi = parsed.get("missing_information")
        if not isinstance(mi, list):
            parsed["missing_information"] = []
        else:
            for item in mi:
                if isinstance(item, dict):
                    if item.get("category") not in _MISSING_CATEGORIES:
                        item["category"] = "labs"

        # ── Citations ────────────────────────────────────────────────
        citations = parsed.get("citations")
        if not isinstance(citations, list):
            parsed["citations"] = []
        else:
            seen_ids = set()
            for i, cit in enumerate(citations):
                if isinstance(cit, dict):
                    # Ensure unique IDs
                    cid = cit.get("id", f"c{i+1}")
                    if cid in seen_ids:
                        cid = f"c{i+1}_{cid}"
                    seen_ids.add(cid)
                    cit["id"] = cid
                    # Normalize source_type
                    if cit.get("source_type") not in _SOURCE_TYPES:
                        cit["source_type"] = "web"

        return parsed

    def _fallback_response(self, raw_text: str) -> Dict[str, Any]:
        """
        Provides a fallback dictionary when AI response parsing fails.
        Returns a valid v2 schema structure.
        """
        return {
            "summary": {
                "overview": raw_text[:3000] if raw_text else "AI response could not be parsed.",
                "severity": "moderate"
            },
            "supporting_findings": [],
            "contradictory_findings": [],
            "differentials": [],
            "next_steps": [],
            "missing_information": [{
                "item": "Parse error",
                "category": "labs",
                "why_it_matters": "The AI response could not be parsed into structured format. The raw response has been placed in the clinical summary.",
                "impact_on_assessment": "All sections may be incomplete or empty.",
                "possible_implications": "Please regenerate the report.",
            }],
            "citations": []
        }

    def merge_grounding_citations(
        self,
        parsed: Dict[str, Any],
        grounding_citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merges grounding citations (from the search-grounded model call)
        into the structured citations array with unique IDs.
        """
        existing_citations = parsed.get("citations", [])
        existing_ids = {c.get("id") for c in existing_citations if isinstance(c, dict)}

        for i, gc in enumerate(grounding_citations):
            if not isinstance(gc, dict):
                continue
            cid = f"g{i+1}"
            while cid in existing_ids:
                cid = f"g{i+1}_{i}"
            existing_ids.add(cid)

            existing_citations.append({
                "id": cid,
                "label": (gc.get("citation_text") or "Source")[:40],
                "source_type": "web",
                "url": gc.get("url", ""),
                "title": gc.get("citation_text", ""),
                "journal": None,
                "year": None,
                "authors": None,
            })

        parsed["citations"] = existing_citations
        return parsed
