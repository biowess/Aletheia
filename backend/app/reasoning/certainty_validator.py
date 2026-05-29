import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CertaintyValidator:
    """
    Enforces epistemically disciplined boundaries on the AI's diagnostic reasoning.
    Ensures that reasoning_confidence never overrides evidence_confidence,
    downgrades certainty based on contradictions, missing confirmation, and weak support.
    """

    def apply_certainty_policies(self, parsed_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and adjusts certainty tiers, confidence levels, and phrasing.
        """
        if not parsed_response or "differentials" not in parsed_response:
            return parsed_response
            
        for diff in parsed_response["differentials"]:
            if not isinstance(diff, dict):
                continue
                
            reasoning_conf = diff.get("reasoning_confidence", 0.5)
            evidence_conf = diff.get("evidence_confidence", 0.5)
            is_provisional = diff.get("is_provisional", False)
            certainty_tier = diff.get("certainty_tier", "possible")
            
            # Rule 1: Reasoning confidence may never override evidence confidence
            if evidence_conf < reasoning_conf:
                logger.info(f"[CERTAINTY POLICY] Downgrading reasoning_confidence ({reasoning_conf}) to match evidence_confidence ({evidence_conf}) for diagnosis: {diff.get('diagnosis')}")
                reasoning_conf = evidence_conf
                diff["reasoning_confidence"] = reasoning_conf
                
                # Soften certainty tier if evidence is weak
                if evidence_conf < 0.5 and certainty_tier in ["likely", "highly likely", "confirmed only if strict conditions are fully met"]:
                    diff["certainty_tier"] = "possible"
                    
            # Rule 2: If provisional, it can never be confirmed or highly likely
            if is_provisional and certainty_tier in ["highly likely", "confirmed only if strict conditions are fully met"]:
                logger.info(f"[CERTAINTY POLICY] Enforcing provisional status for diagnosis: {diff.get('diagnosis')}")
                diff["certainty_tier"] = "provisional classification-compatible"
                
                # Also cap confidence
                if reasoning_conf > 0.75:
                    reasoning_conf = 0.75
                    diff["reasoning_confidence"] = reasoning_conf
                    diff["evidence_confidence"] = min(evidence_conf, 0.75)
            
            # Rule 3: Contradictory evidence should soften certainty
            contradictory_evidence = diff.get("contradictory_evidence", [])
            if contradictory_evidence and len(contradictory_evidence) > 0:
                if certainty_tier == "confirmed only if strict conditions are fully met":
                    diff["certainty_tier"] = "highly likely"
                    logger.info(f"[CERTAINTY POLICY] Softening 'confirmed' to 'highly likely' due to contradictions in {diff.get('diagnosis')}")

            # Rule 4: Compute legacy confidence fallback (take the minimum of both)
            diff["confidence"] = min(reasoning_conf, evidence_conf)
            
            # Rule 5: Safety language enforcement in reasoning text (basic check)
            reasoning = diff.get("reasoning", "")
            if is_provisional or evidence_conf < 0.75:
                # Basic string replacement to soften overconfident claims
                overconfident_terms = ["diagnostic for", "proves", "definitive", "ruled in"]
                for term in overconfident_terms:
                    if term in reasoning.lower():
                        logger.info(f"[CERTAINTY POLICY] Replacing overconfident term '{term}' in reasoning for {diff.get('diagnosis')}")
                        reasoning = re.sub(rf'\b{term}\b', 'suggestive of', reasoning, flags=re.IGNORECASE)
                
                # Handle "confirmed" specially
                if "confirmed" in reasoning.lower():
                    logger.info(f"[CERTAINTY POLICY] Replacing overconfident term 'confirmed' in reasoning for {diff.get('diagnosis')}")
                    reasoning = re.sub(r'\bconfirmed\b', 'supports', reasoning, flags=re.IGNORECASE)
                    
                diff["reasoning"] = reasoning

        return parsed_response
