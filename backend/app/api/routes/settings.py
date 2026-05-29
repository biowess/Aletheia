from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.app_settings_service import AppSettingsService
from app.schemas.app_settings import (
    AppSettingResponse,
    AppSettingUpdateRequest,
    AppSettingsBulkResponse,
)

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=AppSettingsBulkResponse)
async def get_all_settings(
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all application settings.
    """
    try:
        settings = await AppSettingsService.get_all_settings(db)
        return AppSettingsBulkResponse(settings=settings)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{key}", response_model=AppSettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific application setting by key.
    """
    try:
        setting = await AppSettingsService.get_setting(db, key)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        return setting
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{key}", response_model=AppSettingResponse)
async def update_setting(
    key: str,
    setting_in: AppSettingUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the value of an existing application setting.
    """
    try:
        setting = await AppSettingsService.update_setting(db, key, setting_in.value)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        return setting
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
