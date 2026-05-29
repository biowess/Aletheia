import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Case(Base):
    """
    Architectural Notes:
    Why JSON columns were chosen over normalized sub-tables for clinical sections:
    
    1. Schema Flexibility: Clinical data structures are highly variable depending on the 
       specialty, patient condition, and specific encounter. JSON columns allow storing 
       semi-structured and dynamic key-value pairs without requiring constant schema migrations 
       whenever a new clinical attribute is needed.
       
    2. Read Performance: A case is often read in its entirety when presented to a clinician. 
       Fetching all case data in a single row without multiple JOINs to sub-tables significantly 
       improves read latency.
       
    3. Aggregate Root Integrity: The clinical sections are intrinsically tied to the case. 
       They are treated as value objects associated directly with the aggregate root (the Case). 
       They rarely need to be queried independently or linked to other entities.
    """
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Clinical Sections
    anamnesis: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    physical_exam: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    laboratory_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    morphological_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
