from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "General Voice Agent Backend",
        "environment": "dev",
        "api_port": settings.api_port,
        "voice_mode": settings.voice_mode,
        "default_company_id": settings.default_company_id,
        "default_persona_id": settings.default_persona_id,
    }
