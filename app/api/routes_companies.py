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
from app.schemas.company_schema import CompanySetupRequest

router = APIRouter()


def uuid_to_str(value):
    return str(value) if value is not None else None


@router.post("/setup")
async def setup_company(payload: CompanySetupRequest, db: AsyncSession = Depends(get_db)):
    company = Company(
        name=payload.name,
        industry=payload.industry,
        use_case=payload.use_case,
        status=payload.status,
        config={
            "created_from": "company_setup_api",
            "default_persona_name": payload.default_persona_name,
        },
    )

    db.add(company)
    await db.flush()

    ai_settings = CompanyAISettings(
        company_id=company.id,
        llm_provider=payload.ai_settings.llm_provider,
        llm_model=payload.ai_settings.llm_model,
        temperature=payload.ai_settings.temperature,
        system_prompt=payload.ai_settings.system_prompt,
    )

    voice_settings = CompanyVoiceSettings(
        company_id=company.id,
        voice_mode=payload.voice_settings.voice_mode,
        stt_provider=payload.voice_settings.stt_provider,
        stt_model=payload.voice_settings.stt_model,
        tts_provider=payload.voice_settings.tts_provider,
        tts_model=payload.voice_settings.tts_model,
        voice_id=payload.voice_settings.voice_id,
        language=payload.voice_settings.language,
    )

    phone_settings = CompanyPhoneSettings(
        company_id=company.id,
        phone_provider=payload.phone_settings.phone_provider,
        twilio_processing_mode=payload.phone_settings.twilio_processing_mode,
        twilio_phone_number=payload.phone_settings.twilio_phone_number,
        webhook_url=payload.phone_settings.webhook_url,
    )

    feature_flags = CompanyFeatureFlags(
        company_id=company.id,
        enable_text_chat=payload.feature_flags.enable_text_chat,
        enable_voice_chat=payload.feature_flags.enable_voice_chat,
        enable_phone_calling=payload.feature_flags.enable_phone_calling,
        enable_realtime_streaming=payload.feature_flags.enable_realtime_streaming,
        enable_human_handoff=payload.feature_flags.enable_human_handoff,
        enable_call_recording=payload.feature_flags.enable_call_recording,
    )

    default_persona = Persona(
        company_id=company.id,
        name=payload.default_persona_name,
        system_prompt=payload.ai_settings.system_prompt,
        voice=payload.voice_settings.voice_id,
        model=payload.ai_settings.llm_model,
        temperature=str(payload.ai_settings.temperature),
        config={
            "llm_provider": payload.ai_settings.llm_provider,
            "voice_mode": payload.voice_settings.voice_mode,
            "stt_provider": payload.voice_settings.stt_provider,
            "tts_provider": payload.voice_settings.tts_provider,
        },
        is_active=True,
    )

    db.add_all([
        ai_settings,
        voice_settings,
        phone_settings,
        feature_flags,
        default_persona,
    ])

    await db.commit()

    return {
        "message": "Company setup created successfully",
        "company_id": uuid_to_str(company.id),
        "company_name": company.name,
        "default_persona_id": uuid_to_str(default_persona.id),
        "use_case": company.use_case,
        "selected_stack": {
            "llm": {
                "provider": ai_settings.llm_provider,
                "model": ai_settings.llm_model,
            },
            "stt": {
                "provider": voice_settings.stt_provider,
                "model": voice_settings.stt_model,
            },
            "tts": {
                "provider": voice_settings.tts_provider,
                "model": voice_settings.tts_model,
                "voice_id": voice_settings.voice_id,
            },
            "voice_mode": voice_settings.voice_mode,
            "phone_provider": phone_settings.phone_provider,
            "twilio_processing_mode": phone_settings.twilio_processing_mode,
        },
    }


@router.get("/")
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).order_by(Company.created_at.desc()))
    companies = result.scalars().all()

    return [
        {
            "id": uuid_to_str(company.id),
            "name": company.name,
            "industry": company.industry,
            "use_case": company.use_case,
            "status": company.status,
            "created_at": company.created_at,
        }
        for company in companies
    ]


@router.get("/{company_id}/config")
async def get_company_config(company_id: UUID, db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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
        select(Persona).where(Persona.company_id == company_id, Persona.is_active == True)
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
        "default_persona": {
            "id": uuid_to_str(persona.id) if persona else None,
            "name": persona.name if persona else None,
            "model": persona.model if persona else None,
            "voice": persona.voice if persona else None,
        },
    }
