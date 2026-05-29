"""
Pydantic schemas for AppSettings.
Provides models for updating and retrieving application configuration settings.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class AppSettingResponse(BaseModel):
    """Schema for serializing AppSettings ORM model to API response."""
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    value_type: str
    label: str
    description: Optional[str] = None
    updated_at: datetime

class AppSettingUpdateRequest(BaseModel):
    """Schema for updating an individual application setting."""
    value: str

class AppSettingsBulkResponse(BaseModel):
    """Schema for returning a bulk collection of application settings."""
    settings: List[AppSettingResponse] = Field(default_factory=list)
