"""
Pydantic schemas for EvidenceCache.
Provides models for requesting evidence cache lookups and serializing
EvidenceCache ORM responses.
"""
from datetime import datetime
from typing import List, Any
from pydantic import BaseModel, ConfigDict, Field

class EvidenceCacheResponse(BaseModel):
    """Schema for serializing EvidenceCache ORM model to API response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    cache_key: str
    query_text: str
    retrieved_at: datetime
    expires_at: datetime
    response_text: str
    citations: List[Any] = Field(default_factory=list)
    source_urls: List[Any] = Field(default_factory=list)
    ai_provider: str
    is_valid: bool

class EvidenceQueryRequest(BaseModel):
    """Schema for requesting evidence cache lookups."""
    query_text: str
    force_refresh: bool = False
