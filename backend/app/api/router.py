from fastapi import APIRouter
from app.api.routes import cases_router
from app.api.routes.follow_ups import router as follow_ups_router
from app.api.routes.settings import router as settings_router
from app.api.routes.reasoning import router as reasoning_router
from app.api.routes.export import router as export_router
from app.api.routes.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(cases_router)
api_router.include_router(follow_ups_router)
api_router.include_router(settings_router)
api_router.include_router(reasoning_router)
api_router.include_router(export_router)
api_router.include_router(admin_router)
