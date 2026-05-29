"""
Pydantic schemas for the Reasoning Service.
Defines the core ReasoningRequest payload triggering AI reasoning,
the response schema, and internal preprocessing results.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

from .case import (
    AnamnesisSchema,
    PhysicalExamSchema,
    LaboratoryDataSchema,
    MorphologicalDataSchema,
)

class ReasoningRequest(BaseModel):
    """The central payload sent by the frontend to trigger clinical reasoning."""
    case_id: str
    anamnesis: AnamnesisSchema
    physical_exam: PhysicalExamSchema
    laboratory_data: LaboratoryDataSchema
    morphological_data: MorphologicalDataSchema
    follow_up_context: Optional[str] = None
    use_grounding: bool = True
    force_cache_refresh: bool = False

class ReasoningResponse(BaseModel):
    """Schema for the API response indicating the result of a reasoning trigger."""
    report_version_id: str
    case_id: str
    version_number: int
    status: str
    message: Optional[str] = None

class PreprocessingResult(BaseModel):
    """Internal schema for holding the output of the preprocessing engine."""
    anemia_classification: Optional[str] = None
    cytopenias: List[str] = Field(default_factory=list)
    inflammatory_pattern: Optional[str] = None
    metabolic_flags: List[str] = Field(default_factory=list)
    interpretations: List[str] = Field(default_factory=list)
