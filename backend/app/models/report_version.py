import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, String, Boolean, DateTime, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReportVersion(Base):
    """
    Architectural Notes:
    Why ReportVersion is an immutable append-only record:
    
    1. Auditability & Reproducibility: AI-generated reasoning can evolve over time as new case
       information is added. Storing immutable snapshots of the AI report ensures we can trace
       exactly what differential diagnoses and reasoning were presented to the clinician at a given
       point in time.
       
    2. Medical Legal Considerations: In clinical systems, it is crucial to never silently overwrite
       previous AI suggestions that a clinician might have seen or acted upon. Creating a new
       version preserves the historical record.
       
    3. Structural Simplicity: By omitting an updated_at column and strictly enforcing append-only
       operations, we eliminate the complexities of versioning individual fields. Entire snapshots
       are lightweight enough to store as individual rows.
       
    Schema v2 (Structured Report):
    All report sections are stored as typed JSON objects/arrays, never as free-form text.
    The frontend renders directly from these typed structures.
    """
    __tablename__ = "report_versions"
    __table_args__ = (
        UniqueConstraint("case_id", "version_number", name="uq_report_version_case_version"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # ── Structured Report Sections (v2) ──────────────────────────────────────
    
    # JSON object: {"overview": str, "severity": str}
    summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # JSON array of: {"finding": str, "explanation": str, "strength": str}
    supporting_findings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # JSON array of: {"finding": str, "explanation": str, "significance": str}
    contradictory_findings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # JSON array of: {"diagnosis": str, "confidence": float, "reasoning": str, ...}
    differentials: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # JSON array of: {"title": str, "category": str, "rationale": str, "urgency": str, ...}
    next_steps: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # JSON array of: {"item": str, "category": str, "why_it_matters": str, ...}
    missing_information: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # JSON array of: {"id": str, "label": str, "source_type": str, "url": str, "title": str, ...}
    citations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # JSON object with deterministic preprocessing results
    preprocessing_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    ai_provider: Mapped[str] = mapped_column(String, nullable=False)
    ai_model: Mapped[str] = mapped_column(String, nullable=False)
    grounding_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
