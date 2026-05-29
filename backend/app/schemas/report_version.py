"""
Pydantic schemas for the Report Version API responses.

These schemas define the exact typed shape of a structured clinical report.
Every section of the report is a typed object — no free-form text blobs.
The LLM is instructed to produce JSON matching these shapes, the parser validates
and normalizes output against them, and the frontend renders directly from them.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal


# ──────────────────────────────────────────────────────────────────────────────
# Citation
# ──────────────────────────────────────────────────────────────────────────────

from typing import Any
import uuid

class Citation(BaseModel):
    """A strictly verified clinical citation with full provenance metadata."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: f"fallback-{uuid.uuid4().hex[:8]}", description="Unique citation identifier, e.g. 'c1'")
    sourceType: Literal["pubmed", "doi", "guideline", "journal", "web"] = Field(alias="source_type", default="pubmed")
    title: str = ""
    authors: List[str] = Field(default_factory=list)
    journal: str = ""
    year: Optional[int] = None
    verified: bool = True
    pmid: Optional[str] = None
    doi: Optional[str] = None
    canonicalUrl: str = Field(alias="canonical_url", default="")
    sourceDomain: str = Field(alias="source_domain", default="")
    abstractSnippet: Optional[str] = Field(alias="abstract_snippet", default=None)
    evidenceLevel: str = Field(alias="evidence_level", default="case_report")
    label: Optional[str] = None
    url: Optional[str] = None
    vancouver_string: Optional[str] = Field(alias="vancouverString", default=None)

    @model_validator(mode="before")
    @classmethod
    def preprocess_data(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return {"id": f"fallback-{uuid.uuid4().hex[:8]}", "title": str(data)}
        
        # If year is 0, we can leave it as 0, or convert to None. Optional[int] will accept 0.
        # But if we need to explicitly accept it, int accepts 0.
        return data


# ──────────────────────────────────────────────────────────────────────────────
# Clinical Summary
# ──────────────────────────────────────────────────────────────────────────────

class ClinicalSummary(BaseModel):
    """
    Top-level clinical synthesis. The `overview` field may contain
    inline citation tokens of the form {{cite:ID}} which the frontend
    renderer replaces with interactive CitationChip components.
    """
    overview: str = Field(..., description="Rich clinical narrative with {{cite:ID}} tokens")
    severity: Literal["low", "moderate", "high", "critical"] = "moderate"


# ──────────────────────────────────────────────────────────────────────────────
# Findings
# ──────────────────────────────────────────────────────────────────────────────

class SupportingFinding(BaseModel):
    """An evidence-based finding supporting the clinical assessment."""
    finding: str
    explanation: str
    strength: Literal["weak", "moderate", "strong"] = "moderate"


class ContradictoryFinding(BaseModel):
    """A finding that contradicts or complicates the primary assessment."""
    finding: str
    explanation: str
    significance: str


# ──────────────────────────────────────────────────────────────────────────────
# Differential Diagnosis
# ──────────────────────────────────────────────────────────────────────────────

class DifferentialDiagnosis(BaseModel):
    """A ranked differential diagnosis with numeric confidence and reasoned evidence."""
    diagnosis: str
    
    # ── Backward Compatible Fallback ──
    confidence: float = Field(..., ge=0.0, le=1.0, description="0.0–1.0 legacy confidence score fallback")
    
    # ── New Certainty Control Layer ──
    reasoning_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Clinical coherence score")
    evidence_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Literature support score")
    certainty_tier: Literal[
        "possible",
        "likely",
        "highly likely",
        "provisional classification-compatible",
        "confirmed only if strict conditions are fully met"
    ] = Field(default="possible", description="Explicit language tier for diagnostic certainty")
    is_provisional: bool = Field(default=False, description="True if missing longitudinal/repeat confirmation")
    
    reasoning: str = Field(..., description="Clinical reasoning narrative for this diagnosis")
    supporting_evidence: List[str] = Field(default_factory=list)
    contradictory_evidence: List[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# Next Steps
# ──────────────────────────────────────────────────────────────────────────────

class NextStep(BaseModel):
    """
    A clinically actionable recommendation. Each must include specialist-level
    rationale, urgency classification, expected outcome, and risk of delay.
    """
    title: str
    category: Literal["diagnostic", "monitoring", "treatment", "referral", "follow_up"] = "diagnostic"
    rationale: str = Field(..., description="2–5 sentence specialist-level reasoning")
    urgency: Literal["routine", "urgent", "emergent"] = "routine"
    expected_outcome: str = ""
    risks_of_delay: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# Missing Information
# ──────────────────────────────────────────────────────────────────────────────

class MissingInformation(BaseModel):
    """
    A piece of clinical data that is absent from the case and limits the
    assessment. Each entry must explain clinical significance and impact.
    """
    item: str
    category: Literal[
        "history", "labs", "medications", "imaging",
        "risk_factors", "family_history", "physical_exam"
    ] = "labs"
    why_it_matters: str = ""
    impact_on_assessment: str = ""
    possible_implications: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Top-Level Report Version Response
# ──────────────────────────────────────────────────────────────────────────────

class ReportVersionResponse(BaseModel):
    """
    The complete structured clinical report returned by the API.
    Every field is a typed object or typed array — no raw text blobs.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    version_number: int
    created_at: datetime

    summary: ClinicalSummary
    supporting_findings: List[SupportingFinding]
    contradictory_findings: List[ContradictoryFinding]
    differentials: List[DifferentialDiagnosis]
    next_steps: List[NextStep]
    missing_information: List[MissingInformation]
    citations: List[Citation]

    preprocessing_summary: dict = Field(default_factory=dict)

    ai_provider: str
    ai_model: str
    grounding_used: bool
