from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.db.database import get_db
from app.db.mongo import get_mongo_database

router = APIRouter()


def require_admin_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    if not settings.admin_api_key:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY is not configured")

    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    return True


def present(value):
    if not value:
        return False

    lowered = str(value).strip().lower()

    if not lowered:
        return False

    bad_words = ["your_", "replace_", "paste_", "here", "string"]

    return not any(word in lowered for word in bad_words)


@router.get("/readiness")
async def system_readiness(
    _: bool = Depends(require_admin_key),
    db: AsyncSession = Depends(get_db),
):
    checks = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = {"status": "ok"}
    except Exception as exc:
        checks["postgres"] = {"status": "failed", "error": str(exc)}

    try:
        mongo_db = get_mongo_database()
        if mongo_db is None:
            checks["mongodb"] = {"status": "not_configured"}
        else:
            result = await mongo_db.command("ping")
            checks["mongodb"] = {"status": "ok", "result": result}
    except Exception as exc:
        checks["mongodb"] = {"status": "failed", "error": str(exc)}

    checks["providers"] = {
        "openai": present(getattr(settings, "openai_api_key", None)),
        "openrouter": present(getattr(settings, "openrouter_api_key", None)),
        "huggingface": present(getattr(settings, "hf_token", None)) or present(getattr(settings, "huggingface_api_key", None)),
        "anthropic": present(getattr(settings, "anthropic_api_key", None)),
        "gemini": present(getattr(settings, "gemini_api_key", None)) or present(getattr(settings, "google_api_key", None)),
        "bedrock": present(getattr(settings, "aws_access_key_id", None)) and present(getattr(settings, "aws_bedrock_model_id", None)),
        "deepgram": present(getattr(settings, "deepgram_api_key", None)),
        "elevenlabs": present(getattr(settings, "elevenlabs_api_key", None)),
        "azure_speech": present(getattr(settings, "azure_speech_key", None)) and present(getattr(settings, "azure_speech_region", None)),
        "cartesia": present(getattr(settings, "cartesia_api_key", None)) and present(getattr(settings, "cartesia_voice_id", None)),
        "ollama": present(getattr(settings, "ollama_base_url", None)),
    }

    try:
        base_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url.rstrip('/')}/api/tags")

        checks["ollama_runtime"] = {
            "status": "ok" if response.status_code == 200 else "failed",
            "status_code": response.status_code,
        }
    except Exception as exc:
        checks["ollama_runtime"] = {
            "status": "not_reachable",
            "error": str(exc),
        }

    checks["twilio"] = {
        "webhook_base_url_configured": present(getattr(settings, "twilio_webhook_base_url", None)),
        "auth_token_configured": present(getattr(settings, "twilio_auth_token", None)),
        "signature_validation": getattr(settings, "twilio_validate_signatures", False),
    }

    checks["dashboard"] = {
        "status": "available",
        "url": "/admin/dashboard",
    }

    critical_ok = (
        checks["postgres"]["status"] == "ok"
        and checks["mongodb"]["status"] == "ok"
    )

    return {
        "status": "ready" if critical_ok else "degraded",
        "checks": checks,
    }
