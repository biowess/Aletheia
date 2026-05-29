from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.case_service import CaseService, CaseServiceError
from app.schemas.case import (
    CaseCreateRequest,
    CaseUpdateRequest,
    CaseResponse,
    CaseListResponse,
)

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new clinical case.
    """
    try:
        case = await CaseService.create_case(db, case_in)
        return case
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=list[CaseListResponse])
async def list_cases(
    include_archived: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of cases. Optionally include archived cases.
    """
    try:
        cases = await CaseService.list_cases(db, include_archived=include_archived)
        return cases
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific case by its ID.
    """
    try:
        case = await CaseService.get_case(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return case
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_in: CaseUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing case.
    """
    try:
        case = await CaseService.update_case(db, case_id, case_in)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return case
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/archive", response_model=CaseResponse)
async def archive_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Archive a specific case.
    """
    try:
        case = await CaseService.archive_case(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return case
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{case_id}/unarchive", response_model=CaseResponse)
async def unarchive_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Unarchive a specific case.
    """
    try:
        case = await CaseService.unarchive_case(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        return case
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific case permanently.
    """
    try:
        success = await CaseService.delete_case(db, case_id)
        if not success:
            raise HTTPException(status_code=404, detail="Case not found")
        return {"deleted": True}
    except CaseServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
