from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AnamnesisSchema(BaseModel):
    chief_complaint: Optional[str] = Field(default=None, max_length=5000)
    history_of_present_illness: Optional[str] = Field(default=None, max_length=5000)
    past_medical_history: Optional[str] = Field(default=None, max_length=5000)
    medications: Optional[str] = Field(default=None, max_length=5000)
    allergies: Optional[str] = Field(default=None, max_length=5000)
    family_history: Optional[str] = Field(default=None, max_length=5000)
    social_history: Optional[str] = Field(default=None, max_length=5000)
    travel_history: Optional[str] = Field(default=None, max_length=5000)
    constitutional_symptoms: Optional[str] = Field(default=None, max_length=5000)

class PhysicalExamSchema(BaseModel):
    general_appearance: Optional[str] = Field(default=None, max_length=5000)
    heent: Optional[str] = Field(default=None, max_length=5000)
    neck: Optional[str] = Field(default=None, max_length=5000)
    cardiovascular: Optional[str] = Field(default=None, max_length=5000)
    respiratory: Optional[str] = Field(default=None, max_length=5000)
    abdominal: Optional[str] = Field(default=None, max_length=5000)
    neurologic: Optional[str] = Field(default=None, max_length=5000)
    psychiatric: Optional[str] = Field(default=None, max_length=5000)
    vascular: Optional[str] = Field(default=None, max_length=5000)
    genitourinary: Optional[str] = Field(default=None, max_length=5000)
    endocrine: Optional[str] = Field(default=None, max_length=5000)
    dermatologic: Optional[str] = Field(default=None, max_length=5000)
    lymphatic: Optional[str] = Field(default=None, max_length=5000)
    musculoskeletal: Optional[str] = Field(default=None, max_length=5000)
    breast: Optional[str] = Field(default=None, max_length=5000)
    pelvic: Optional[str] = Field(default=None, max_length=5000)
    rectal: Optional[str] = Field(default=None, max_length=5000)

class LaboratoryDataSchema(BaseModel):
    cbc: Optional[str] = Field(default=None, max_length=5000)
    differential: Optional[str] = Field(default=None, max_length=5000)
    coagulation: Optional[str] = Field(default=None, max_length=5000)
    chemistry: Optional[str] = Field(default=None, max_length=5000)
    inflammatory_markers: Optional[str] = Field(default=None, max_length=5000)
    iron_studies: Optional[str] = Field(default=None, max_length=5000)
    hemolysis_markers: Optional[str] = Field(default=None, max_length=5000)
    endocrine_panels: Optional[str] = Field(default=None, max_length=5000)

class MorphologicalDataSchema(BaseModel):
    xray: Optional[str] = Field(default=None, max_length=5000)
    ct: Optional[str] = Field(default=None, max_length=5000)
    mri: Optional[str] = Field(default=None, max_length=5000)
    ultrasound: Optional[str] = Field(default=None, max_length=5000)
    pathology: Optional[str] = Field(default=None, max_length=5000)
    peripheral_smear: Optional[str] = Field(default=None, max_length=5000)
    biopsy: Optional[str] = Field(default=None, max_length=5000)
    flow_cytometry: Optional[str] = Field(default=None, max_length=5000)

class CaseCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    anamnesis: AnamnesisSchema = Field(default_factory=AnamnesisSchema)
    physical_exam: PhysicalExamSchema = Field(default_factory=PhysicalExamSchema)
    laboratory_data: LaboratoryDataSchema = Field(default_factory=LaboratoryDataSchema)
    morphological_data: MorphologicalDataSchema = Field(default_factory=MorphologicalDataSchema)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(default=None, max_length=10000)

class CaseUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    anamnesis: Optional[AnamnesisSchema] = None
    physical_exam: Optional[PhysicalExamSchema] = None
    laboratory_data: Optional[LaboratoryDataSchema] = None
    morphological_data: Optional[MorphologicalDataSchema] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=10000)

class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str = Field(..., max_length=200)
    anamnesis: AnamnesisSchema
    physical_exam: PhysicalExamSchema
    laboratory_data: LaboratoryDataSchema
    morphological_data: MorphologicalDataSchema
    tags: List[str]
    notes: Optional[str] = Field(default=None, max_length=10000)
    created_at: datetime
    updated_at: datetime
    is_archived: bool

class CaseListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str = Field(..., max_length=200)
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    tags: List[str]
