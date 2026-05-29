import pytest
from app.reasoning.certainty_validator import CertaintyValidator

def test_overconfident_diagnosis_is_downgraded():
    validator = CertaintyValidator()
    response = {
        "differentials": [
            {
                "diagnosis": "Lupus",
                "reasoning_confidence": 0.9,
                "evidence_confidence": 0.4,
                "certainty_tier": "highly likely",
                "is_provisional": False
            }
        ]
    }
    
    validated = validator.apply_certainty_policies(response)
    diff = validated["differentials"][0]
    
    assert diff["reasoning_confidence"] == 0.4
    assert diff["evidence_confidence"] == 0.4
    assert diff["certainty_tier"] == "possible"
    assert diff["confidence"] == 0.4


def test_definitive_language_blocked_when_missing_data():
    validator = CertaintyValidator()
    response = {
        "differentials": [
            {
                "diagnosis": "Antiphospholipid Syndrome",
                "reasoning_confidence": 0.85,
                "evidence_confidence": 0.9,
                "certainty_tier": "confirmed only if strict conditions are fully met",
                "is_provisional": True,
                "reasoning": "This is diagnostic for APS and definitive."
            }
        ]
    }
    
    validated = validator.apply_certainty_policies(response)
    diff = validated["differentials"][0]
    
    assert diff["certainty_tier"] == "provisional classification-compatible"
    assert diff["reasoning_confidence"] == 0.75
    assert diff["evidence_confidence"] == 0.75
    assert "suggestive of" in diff["reasoning"]
    assert "diagnostic for" not in diff["reasoning"]


def test_contradictory_evidence_preserves_and_softens():
    validator = CertaintyValidator()
    response = {
        "differentials": [
            {
                "diagnosis": "Rheumatoid Arthritis",
                "reasoning_confidence": 0.8,
                "evidence_confidence": 0.8,
                "certainty_tier": "confirmed only if strict conditions are fully met",
                "is_provisional": False,
                "contradictory_evidence": ["Negative RF and ACPA"]
            }
        ]
    }
    
    validated = validator.apply_certainty_policies(response)
    diff = validated["differentials"][0]
    
    assert diff["certainty_tier"] == "highly likely"
    assert "Negative RF and ACPA" in diff["contradictory_evidence"]


def test_legacy_confidence_fallback():
    validator = CertaintyValidator()
    response = {
        "differentials": [
            {
                "diagnosis": "Osteoarthritis",
                "reasoning_confidence": 0.7,
                "evidence_confidence": 0.9,
                "certainty_tier": "likely",
                "is_provisional": False
            }
        ]
    }
    
    validated = validator.apply_certainty_policies(response)
    diff = validated["differentials"][0]
    
    # Minimum of reasoning (0.7) and evidence (0.9)
    assert diff["confidence"] == 0.7
