from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from .case import (
    AnamnesisSchema,
    PhysicalExamSchema,
    LaboratoryDataSchema,
    MorphologicalDataSchema
)

class FollowUpCreateRequest(BaseModel):
    entry_type: Literal["anamnesis", "physical_exam", "laboratory", "imaging", "procedure", "general_note", "other"]
    title: str
    
    anamnesis_delta: Optional[AnamnesisSchema] = None
    physical_exam_delta: Optional[PhysicalExamSchema] = None
    laboratory_delta: Optional[LaboratoryDataSchema] = None
    morphological_delta: Optional[MorphologicalDataSchema] = None
    
    free_text_note: Optional[str] = None

class FollowUpEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    created_at: datetime
    
    entry_type: str
    title: str
    
    anamnesis_delta: dict
    physical_exam_delta: dict
    laboratory_delta: dict
    morphological_delta: dict
    
    free_text_note: Optional[str] = None
    triggered_report_id: Optional[UUID] = None
