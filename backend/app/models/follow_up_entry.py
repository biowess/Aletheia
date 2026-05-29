import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, JSON, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FollowUpEntry(Base):
    """
    Architectural Notes:
    Append-Only Design for Follow-Up Entries
    
    1. Immutable History: Follow-up entries represent discrete events or updates in the 
       clinical timeline. By making them append-only and immutable (no updated_at column, 
       no deletion), we preserve a strict, auditable history of how a clinical case evolved.
    
    2. Delta Storage: Instead of duplicating the entire case state at each step, follow-ups 
       store only the incremental changes (deltas) for anamnesis, physical exam, labs, and 
       imaging. This is storage-efficient and highlights exactly what new information was 
       introduced during the specific follow-up.
    
    3. Event Sourcing Pattern: This structure lightly mirrors an event-sourcing approach. 
       The current state of a case can be seen as its initial state plus all chronological 
       follow-up deltas applied sequentially.
    """
    __tablename__ = "follow_up_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("cases.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    entry_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    
    # Delta fields
    anamnesis_delta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    physical_exam_delta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    laboratory_delta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    morphological_delta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    free_text_note: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    triggered_report_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("report_versions.id"), 
        nullable=True
    )
