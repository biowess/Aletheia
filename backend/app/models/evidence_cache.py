import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EvidenceCache(Base):
    """
    Architectural Notes:
    Caching Strategy:
    
    1. Global De-duplication: The EvidenceCache is intentionally not tied to a specific Case. 
       By caching responses globally using a unique `cache_key` (SHA-256 digest of the normalized query), 
       different users querying for the same medical evidence can benefit from previously retrieved responses,
       minimizing redundant and costly LLM/grounding API calls.
       
    2. TTL Cleanup Efficiency: Storing `expires_at` with an index allows background tasks or 
       cleanup routines to efficiently identify and purge stale data without full table scans, 
       maintaining database performance as the cache grows.
       
    3. Soft Invalidation: The `is_valid` flag allows for programmatic or manual soft invalidation 
       of cache entries (e.g., if a retrieved response is determined to be hallucinated or of low quality),
       while retaining the record for audit or debugging purposes instead of a hard delete.
    """
    __tablename__ = "evidence_cache"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Unique index enforced at the column level
    cache_key: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    query_text: Mapped[str] = mapped_column(String, nullable=False)
    
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Indexed for efficient TTL cleanup queries
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    response_text: Mapped[str] = mapped_column(String, nullable=False)
    
    citations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    source_urls: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    ai_provider: Mapped[str] = mapped_column(String, nullable=False)
    
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
