from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Company, CompanyAISettings, CompanyVoiceSettings

router = APIRouter()


class ProviderConfigPayload(BaseModel):
    llm_provider: str | None = None
    llm_model: str | None = None
    temperature: float | None = None
    system_prompt: str | None = None

    voice_mode: str | None = None
    stt_provider: str | None = None
    stt_model: str | None = None
    tts_provider: str | None = None
    tts_model: str | None = None
    voice_id: str | None = None
    language: str | None = None


ALLOWED_LLM_PROVIDERS = {
    "openai",
    "openrouter",
    "huggingface",
    "hf",
    "anthropic",
    "claude",
    "gemini",
    "google",
    "bedrock",
    "aws_bedrock",
    "ollama",
    "azure_openai",
}

ALLOWED_STT_PROVIDERS = {
    "openai",
    "elevenlabs",
    "deepgram",
    "azure_speech",
    "whisper_cpp",
    "local",
}

ALLOWED_TTS_PROVIDERS = {
    "openai",
    "elevenlabs",
    "deepgram",
    "aws_polly",
    "polly",
    "azure_speech",
    "cartesia",
    "cartesia_sonic",
    "sonic",
    "mac_say",
    "local",
}

ALLOWED_VOICE_MODES = {
    "configured_batch",
    "batch",
    "realtime",
    "twilio_batch",
    "twilio_realtime",
}


def require_admin_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_API_KEY is not configured on the server",
        )

    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin API key",
        )

    return True


def clean_value(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    invalid_values = {
        "string",
        "your_value_here",
        "your_provider_here",
        "your_model_here",
        "null",
        "none",
    }

    if cleaned.lower() in invalid_values:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid placeholder value: {value}",
        )

    return cleaned


def validate_provider(value: str | None, allowed: set[str], field_name: str):
    cleaned = clean_value(value)

    if cleaned is None:
        return None

    normalized = cleaned.lower()

    if normalized not in allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Unsupported {field_name}: {cleaned}",
                "allowed_values": sorted(allowed),
            },
        )

    return normalized


def validate_optional_text(value: str | None, field_name: str):
    cleaned = clean_value(value)

    if cleaned is None:
        return None

    return cleaned


@router.patch("/companies/{company_id}/provider-config")
async def update_provider_config(
    company_id: UUID,
    payload: ProviderConfigPayload,
    _: bool = Depends(require_admin_key),
    db: AsyncSession = Depends(get_db),
):
    llm_provider = validate_provider(
        payload.llm_provider,
        ALLOWED_LLM_PROVIDERS,
        "llm_provider",
    )

    stt_provider = validate_provider(
        payload.stt_provider,
        ALLOWED_STT_PROVIDERS,
        "stt_provider",
    )

    tts_provider = validate_provider(
        payload.tts_provider,
        ALLOWED_TTS_PROVIDERS,
        "tts_provider",
    )

    voice_mode = validate_provider(
        payload.voice_mode,
        ALLOWED_VOICE_MODES,
        "voice_mode",
    )

    llm_model = validate_optional_text(payload.llm_model, "llm_model")
    stt_model = validate_optional_text(payload.stt_model, "stt_model")
    tts_model = validate_optional_text(payload.tts_model, "tts_model")
    voice_id = validate_optional_text(payload.voice_id, "voice_id")
    language = validate_optional_text(payload.language, "language")
    system_prompt = validate_optional_text(payload.system_prompt, "system_prompt")

    if payload.temperature is not None:
        if payload.temperature < 0 or payload.temperature > 2:
            raise HTTPException(
                status_code=400,
                detail="temperature must be between 0 and 2",
            )

    company_result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    ai_result = await db.execute(
        select(CompanyAISettings).where(
            CompanyAISettings.company_id == company_id
        )
    )
    ai_settings = ai_result.scalar_one_or_none()

    if not ai_settings:
        ai_settings = CompanyAISettings(company_id=company_id)
        db.add(ai_settings)
        await db.flush()

    voice_result = await db.execute(
        select(CompanyVoiceSettings).where(
            CompanyVoiceSettings.company_id == company_id
        )
    )
    voice_settings = voice_result.scalar_one_or_none()

    if not voice_settings:
        voice_settings = CompanyVoiceSettings(company_id=company_id)
        db.add(voice_settings)
        await db.flush()

    if llm_provider is not None:
        ai_settings.llm_provider = llm_provider

    if llm_model is not None:
        ai_settings.llm_model = llm_model

    if payload.temperature is not None:
        ai_settings.temperature = payload.temperature

    if system_prompt is not None:
        ai_settings.system_prompt = system_prompt

    if voice_mode is not None:
        voice_settings.voice_mode = voice_mode

    if stt_provider is not None:
        voice_settings.stt_provider = stt_provider

    if stt_model is not None:
        voice_settings.stt_model = stt_model

    if tts_provider is not None:
        voice_settings.tts_provider = tts_provider

    if tts_model is not None:
        voice_settings.tts_model = tts_model

    if voice_id is not None:
        voice_settings.voice_id = voice_id

    if language is not None:
        voice_settings.language = language

    await db.commit()
    await db.refresh(ai_settings)
    await db.refresh(voice_settings)

    return {
        "status": "updated",
        "company_id": str(company_id),
        "ai_settings": {
            "llm_provider": ai_settings.llm_provider,
            "llm_model": ai_settings.llm_model,
            "temperature": ai_settings.temperature,
            "system_prompt": ai_settings.system_prompt,
        },
        "voice_settings": {
            "voice_mode": voice_settings.voice_mode,
            "stt_provider": voice_settings.stt_provider,
            "stt_model": voice_settings.stt_model,
            "tts_provider": voice_settings.tts_provider,
            "tts_model": voice_settings.tts_model,
            "voice_id": voice_settings.voice_id,
            "language": voice_settings.language,
        },
    }
