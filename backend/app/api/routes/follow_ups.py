from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.case_service import CaseService
from app.services.follow_up_service import FollowUpService
from app.schemas.follow_up_entry import (
    FollowUpCreateRequest,
    FollowUpEntryResponse,
)

router = APIRouter(prefix="/cases", tags=["Follow-ups"])

@router.post("/{case_id}/follow-ups", response_model=FollowUpEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_follow_up(
    case_id: str,
    follow_up_in: FollowUpCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new follow-up entry for a specific case.
    """
    case = await CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        entry = await FollowUpService.create_follow_up(db, case_id, follow_up_in)
        return entry
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{case_id}/follow-ups", response_model=list[FollowUpEntryResponse])
async def list_follow_ups(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all follow-up entries for a specific case, ordered chronologically.
    """
    case = await CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        entries = await FollowUpService.list_follow_ups_for_case(db, case_id)
        return entries
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{case_id}/follow-ups/{entry_id}", response_model=FollowUpEntryResponse)
async def get_follow_up(
    case_id: str,
    entry_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific follow-up entry by ID for a specific case.
    """
    case = await CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    try:
        entry = await FollowUpService.get_follow_up(db, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Follow-up entry not found")
        # Ensure the entry belongs to the case
        if str(entry.case_id) != case_id:
            raise HTTPException(status_code=404, detail="Follow-up entry not found for this case")
        return entry
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
