from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import (
    Company,
    CompanyAISettings,
    CompanyVoiceSettings,
    CompanyPhoneSettings,
    CompanyFeatureFlags,
    Persona,
)
from app.core.security import require_admin_api_key
from app.schemas.admin_config_schema import (
    UpdateAISettingsRequest,
    UpdateVoiceSettingsRequest,
    UpdatePhoneSettingsRequest,
    UpdateFeatureFlagsRequest,
)

router = APIRouter(dependencies=[Depends(require_admin_api_key)])


def uuid_to_str(value):
    return str(value) if value is not None else None


async def get_company_or_404(company_id: UUID, db: AsyncSession):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


def apply_updates(model_obj, payload):
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(model_obj, field, value)

    return update_data


@router.get("/companies/{company_id}/full-config")
async def get_full_company_config(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    company = await get_company_or_404(company_id, db)

    ai_result = await db.execute(
        select(CompanyAISettings).where(CompanyAISettings.company_id == company_id)
    )
    ai_settings = ai_result.scalar_one_or_none()

    voice_result = await db.execute(
        select(CompanyVoiceSettings).where(CompanyVoiceSettings.company_id == company_id)
    )
    voice_settings = voice_result.scalar_one_or_none()

    phone_result = await db.execute(
        select(CompanyPhoneSettings).where(CompanyPhoneSettings.company_id == company_id)
    )
    phone_settings = phone_result.scalar_one_or_none()

    flags_result = await db.execute(
        select(CompanyFeatureFlags).where(CompanyFeatureFlags.company_id == company_id)
    )
    feature_flags = flags_result.scalar_one_or_none()

    persona_result = await db.execute(
        select(Persona).where(
            Persona.company_id == company_id,
            Persona.is_active == True,
        )
    )
    persona = persona_result.scalar_one_or_none()

    return {
        "company": {
            "id": uuid_to_str(company.id),
            "name": company.name,
            "industry": company.industry,
            "use_case": company.use_case,
            "status": company.status,
        },
        "ai_settings": {
            "llm_provider": ai_settings.llm_provider if ai_settings else None,
            "llm_model": ai_settings.llm_model if ai_settings else None,
            "temperature": ai_settings.temperature if ai_settings else None,
            "system_prompt": ai_settings.system_prompt if ai_settings else None,
        },
        "voice_settings": {
            "voice_mode": voice_settings.voice_mode if voice_settings else None,
            "stt_provider": voice_settings.stt_provider if voice_settings else None,
            "stt_model": voice_settings.stt_model if voice_settings else None,
            "tts_provider": voice_settings.tts_provider if voice_settings else None,
            "tts_model": voice_settings.tts_model if voice_settings else None,
            "voice_id": voice_settings.voice_id if voice_settings else None,
            "language": voice_settings.language if voice_settings else None,
        },
        "phone_settings": {
            "phone_provider": phone_settings.phone_provider if phone_settings else None,
            "twilio_processing_mode": phone_settings.twilio_processing_mode if phone_settings else None,
            "twilio_phone_number": phone_settings.twilio_phone_number if phone_settings else None,
            "webhook_url": phone_settings.webhook_url if phone_settings else None,
        },
        "feature_flags": {
            "enable_text_chat": feature_flags.enable_text_chat if feature_flags else None,
            "enable_voice_chat": feature_flags.enable_voice_chat if feature_flags else None,
            "enable_phone_calling": feature_flags.enable_phone_calling if feature_flags else None,
            "enable_realtime_streaming": feature_flags.enable_realtime_streaming if feature_flags else None,
            "enable_human_handoff": feature_flags.enable_human_handoff if feature_flags else None,
            "enable_call_recording": feature_flags.enable_call_recording if feature_flags else None,
        },
        "active_persona": {
            "id": uuid_to_str(persona.id) if persona else None,
            "name": persona.name if persona else None,
            "model": persona.model if persona else None,
            "voice": persona.voice if persona else None,
        },
    }


@router.patch("/companies/{company_id}/ai-settings")
async def update_ai_settings(
    company_id: UUID,
    payload: UpdateAISettingsRequest,
    db: AsyncSession = Depends(get_db),
):
    company = await get_company_or_404(company_id, db)

    result = await db.execute(
        select(CompanyAISettings).where(CompanyAISettings.company_id == company_id)
    )
    ai_settings = result.scalar_one_or_none()

    if not ai_settings:
        ai_settings = CompanyAISettings(
            company_id=company_id,
            llm_provider=payload.llm_provider or "openrouter",
            llm_model=payload.llm_model or "openrouter/free",
            temperature=payload.temperature if payload.temperature is not None else 0.7,
            system_prompt=payload.system_prompt or "You are a helpful voice assistant.",
        )
        db.add(ai_settings)
    else:
        apply_updates(ai_settings, payload)

    persona_result = await db.execute(
        select(Persona).where(
            Persona.company_id == company_id,
            Persona.is_active == True,
        )
    )
    persona = persona_result.scalar_one_or_none()

    if persona:
        if payload.llm_model is not None:
            persona.model = payload.llm_model
        if payload.temperature is not None:
            persona.temperature = str(payload.temperature)
        if payload.system_prompt is not None:
            persona.system_prompt = payload.system_prompt

    await db.commit()
    await db.refresh(ai_settings)

    return {
        "message": "AI settings updated successfully",
        "company_id": uuid_to_str(company.id),
        "company_name": company.name,
        "ai_settings": {
            "llm_provider": ai_settings.llm_provider,
            "llm_model": ai_settings.llm_model,
            "temperature": ai_settings.temperature,
            "system_prompt": ai_settings.system_prompt,
        },
    }


@router.patch("/companies/{company_id}/voice-settings")
async def update_voice_settings(
    company_id: UUID,
    payload: UpdateVoiceSettingsRequest,
    db: AsyncSession = Depends(get_db),
):
    company = await get_company_or_404(company_id, db)

    result = await db.execute(
        select(CompanyVoiceSettings).where(CompanyVoiceSettings.company_id == company_id)
    )
    voice_settings = result.scalar_one_or_none()

    if not voice_settings:
        voice_settings = CompanyVoiceSettings(company_id=company_id)
        db.add(voice_settings)

    apply_updates(voice_settings, payload)

    persona_result = await db.execute(
        select(Persona).where(
            Persona.company_id == company_id,
            Persona.is_active == True,
        )
    )
    persona = persona_result.scalar_one_or_none()

    if persona and payload.voice_id is not None:
        persona.voice = payload.voice_id

    await db.commit()
    await db.refresh(voice_settings)

    return {
        "message": "Voice settings updated successfully",
        "company_id": uuid_to_str(company.id),
        "company_name": company.name,
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


@router.patch("/companies/{company_id}/phone-settings")
async def update_phone_settings(
    company_id: UUID,
    payload: UpdatePhoneSettingsRequest,
    db: AsyncSession = Depends(get_db),
):
    company = await get_company_or_404(company_id, db)

    result = await db.execute(
        select(CompanyPhoneSettings).where(CompanyPhoneSettings.company_id == company_id)
    )
    phone_settings = result.scalar_one_or_none()

    if not phone_settings:
        phone_settings = CompanyPhoneSettings(company_id=company_id)
        db.add(phone_settings)

    apply_updates(phone_settings, payload)

    await db.commit()
    await db.refresh(phone_settings)

    return {
        "message": "Phone settings updated successfully",
        "company_id": uuid_to_str(company.id),
        "company_name": company.name,
        "phone_settings": {
            "phone_provider": phone_settings.phone_provider,
            "twilio_processing_mode": phone_settings.twilio_processing_mode,
            "twilio_phone_number": phone_settings.twilio_phone_number,
            "webhook_url": phone_settings.webhook_url,
        },
    }


@router.patch("/companies/{company_id}/feature-flags")
async def update_feature_flags(
    company_id: UUID,
    payload: UpdateFeatureFlagsRequest,
    db: AsyncSession = Depends(get_db),
):
    company = await get_company_or_404(company_id, db)

    result = await db.execute(
        select(CompanyFeatureFlags).where(CompanyFeatureFlags.company_id == company_id)
    )
    feature_flags = result.scalar_one_or_none()

    if not feature_flags:
        feature_flags = CompanyFeatureFlags(company_id=company_id)
        db.add(feature_flags)

    apply_updates(feature_flags, payload)

    await db.commit()
    await db.refresh(feature_flags)

    return {
        "message": "Feature flags updated successfully",
        "company_id": uuid_to_str(company.id),
        "company_name": company.name,
        "feature_flags": {
            "enable_text_chat": feature_flags.enable_text_chat,
            "enable_voice_chat": feature_flags.enable_voice_chat,
            "enable_phone_calling": feature_flags.enable_phone_calling,
            "enable_realtime_streaming": feature_flags.enable_realtime_streaming,
            "enable_human_handoff": feature_flags.enable_human_handoff,
            "enable_call_recording": feature_flags.enable_call_recording,
        },
    }
