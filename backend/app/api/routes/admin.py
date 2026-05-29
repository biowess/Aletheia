from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.evidence_cache import EvidenceCache
from app.services.evidence_cache_service import EvidenceCacheService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/maintenance/cleanup-cache")
async def cleanup_cache(db: AsyncSession = Depends(get_db)):
    deleted_count = await EvidenceCacheService.cleanup_expired_entries(db)
    return {"deleted_entries": deleted_count}

@router.get("/maintenance/cache-stats")
async def cache_stats(db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    
    stmt = select(
        func.count(EvidenceCache.id).label("total_entries"),
        func.count(EvidenceCache.id).filter(EvidenceCache.expires_at < now).label("expired_entries"),
        func.count(EvidenceCache.id).filter(
            (EvidenceCache.expires_at >= now) & (EvidenceCache.is_valid == True)
        ).label("valid_entries")
    )
    
    result = await db.execute(stmt)
    row = result.first()
    
    return {
        "total_entries": getattr(row, "total_entries", 0) or 0,
        "expired_entries": getattr(row, "expired_entries", 0) or 0,
        "valid_entries": getattr(row, "valid_entries", 0) or 0,
    }
