from pathlib import Path
from time import time

from fastapi import APIRouter, Header, HTTPException, Query

from app.core.config import settings

router = APIRouter()


def require_admin_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    if not settings.admin_api_key:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY is not configured")

    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    return True


@router.get("/routes")
async def route_summary():
    return {
        "status": "ok",
        "important_links": {
            "swagger_docs": "/docs",
            "admin_dashboard": "/admin/dashboard",
            "provider_status": "/providers/status",
            "system_readiness": "/system/readiness",
            "analytics_company_summary": "/analytics/company-summary",
            "debug_recent_sessions": "/debug/sessions/recent",
            "debug_recent_errors": "/debug/errors/recent",
            "configured_voice": "/voice/configured-batch",
            "chat": "/chat/message",
            "twilio_batch": "/twilio/voice",
            "twilio_realtime": "/twilio-realtime/stream-twiml",
        },
        "demo_links": {
            "local_voice": "/demo/local_voice.html",
            "openai_voice": "/demo/openai_voice.html",
            "realtime_voice": "/demo/realtime_voice.html",
            "openai_realtime": "/demo/openai_realtime.html",
        },
    }


@router.delete("/generated-audio")
async def cleanup_generated_audio(
    dry_run: bool = Query(default=True),
    max_age_hours: int = Query(default=0, ge=0),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    generated_dir = Path("app/static/generated")
    generated_dir.mkdir(parents=True, exist_ok=True)

    allowed_extensions = {".mp3", ".wav", ".webm", ".ogg", ".m4a", ".mp4"}
    now = time()
    max_age_seconds = max_age_hours * 3600

    matched = []
    deleted = []

    for file_path in generated_dir.iterdir():
        if not file_path.is_file():
            continue

        if file_path.name == ".gitkeep":
            continue

        if file_path.suffix.lower() not in allowed_extensions:
            continue

        age_seconds = now - file_path.stat().st_mtime

        if max_age_hours > 0 and age_seconds < max_age_seconds:
            continue

        matched.append(str(file_path))

        if not dry_run:
            file_path.unlink()
            deleted.append(str(file_path))

    return {
        "status": "ok",
        "dry_run": dry_run,
        "max_age_hours": max_age_hours,
        "matched_count": len(matched),
        "deleted_count": len(deleted),
        "matched_files": matched[:50],
        "deleted_files": deleted[:50],
    }
