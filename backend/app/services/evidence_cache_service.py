import hashlib
import string
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from app.models.evidence_cache import EvidenceCache
from app.core.config import settings

class EvidenceCacheService:
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

    @staticmethod
    def generate_cache_key(query_text: str) -> str:
        """
        Normalizes the query text and returns its SHA-256 hex digest.
        """
        normalized_query = query_text.lower().strip()
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        normalized_query = normalized_query.translate(translator)
        
        # Collapse multiple spaces
        normalized_query = ' '.join(normalized_query.split())
        
        return hashlib.sha256(normalized_query.encode('utf-8')).hexdigest()

    @staticmethod
    async def get_cached_evidence(db: AsyncSession, query_text: str) -> EvidenceCache | None:
        """
        Retrieves a valid, non-expired cache entry for the given query text.
        """
        cache_key = EvidenceCacheService.generate_cache_key(query_text)
        now = datetime.utcnow()
        
        stmt = select(EvidenceCache).where(
            EvidenceCache.cache_key == cache_key,
            EvidenceCache.is_valid == True,
            EvidenceCache.expires_at > now
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def store_evidence(
        db: AsyncSession, 
        query_text: str, 
        response_text: str, 
        citations: list[dict], 
        source_urls: list[str], 
        ai_provider: str,
        ttl_hours: int | None = None
    ) -> EvidenceCache:
        """
        Stores a new evidence cache entry. Handles concurrent insertions gracefully.
        """
        cache_key = EvidenceCacheService.generate_cache_key(query_text)
        now = datetime.utcnow()
        actual_ttl = ttl_hours if ttl_hours is not None else settings.max_evidence_cache_age_hours
        expires_at = now + timedelta(hours=actual_ttl)
        
        cache_entry = EvidenceCache(
            cache_key=cache_key,
            query_text=query_text,
            response_text=response_text,
            citations=citations,
            source_urls=source_urls,
            ai_provider=ai_provider,
            expires_at=expires_at,
            retrieved_at=now,
            is_valid=True
        )
        
        try:
            db.add(cache_entry)
            await db.commit()
            await db.refresh(cache_entry)
            return cache_entry
        except IntegrityError:
            await db.rollback()
            # If we hit an IntegrityError on cache_key, it means another request just cached it.
            # We can safely retrieve that newly cached entry.
            stmt = select(EvidenceCache).where(EvidenceCache.cache_key == cache_key)
            result = await db.execute(stmt)
            existing_entry = result.scalars().first()
            if existing_entry:
                return existing_entry
            raise

    @staticmethod
    async def invalidate_cache_entry(db: AsyncSession, cache_key: str) -> bool:
        """
        Soft invalidates a cache entry by setting is_valid to False.
        """
        stmt = select(EvidenceCache).where(EvidenceCache.cache_key == cache_key)
        result = await db.execute(stmt)
        entry = result.scalars().first()
        
        if entry:
            entry.is_valid = False
            await db.commit()
            return True
        return False

    @staticmethod
    async def cleanup_expired_entries(db: AsyncSession) -> int:
        """
        Deletes all expired cache entries.
        """
        now = datetime.utcnow()
        stmt = delete(EvidenceCache).where(EvidenceCache.expires_at < now)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
