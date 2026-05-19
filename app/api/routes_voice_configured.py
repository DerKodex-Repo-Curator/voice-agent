from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_company_api_key
from app.db.database import get_db
from app.db.models import (
    Company,
    CompanyAISettings,
    CompanyFeatureFlags,
    CompanyVoiceSettings,
    ConversationMessage,
    ConversationSession,
    Persona,
)
from app.services.llm_router import llm_router
from app.services.llm_fallback_router import llm_fallback_router
from app.services.mongo_event_logger import mongo_event_logger
from app.services.error_event_logger import log_error_event
from app.services.latency_tracker import LatencyTracker
from app.services.error_formatting import build_provider_error_detail
from app.services.cost_estimator import estimate_voice_request_cost
from app.services.audio_upload_validator import validate_audio_upload
from app.services.voice_provider_router import voice_provider_router

router = APIRouter()


def uuid_to_str(value):
    return str(value) if value is not None else None


@router.post("/configured-batch")
async def configured_batch_voice_chat(
    company_id: UUID = Form(...),
    session_id: UUID | None = Form(default=None),
    channel: str = Form(default="configured_batch_voice"),
    audio_file: UploadFile = File(...),
    x_company_api_key: str | None = Header(default=None, alias="X-Company-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    require_company_api_key(company_id, x_company_api_key)

    company_result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    flags_result = await db.execute(
        select(CompanyFeatureFlags).where(
            CompanyFeatureFlags.company_id == company_id
        )
    )
    feature_flags = flags_result.scalar_one_or_none()

    if feature_flags and not feature_flags.enable_voice_chat:
        raise HTTPException(
            status_code=403,
            detail="Voice chat is disabled for this company",
        )

    ai_result = await db.execute(
        select(CompanyAISettings).where(
            CompanyAISettings.company_id == company_id
        )
    )
    ai_settings = ai_result.scalar_one_or_none()

    if not ai_settings:
        raise HTTPException(status_code=404, detail="AI settings not found")

    voice_result = await db.execute(
        select(CompanyVoiceSettings).where(
            CompanyVoiceSettings.company_id == company_id
        )
    )
    voice_settings = voice_result.scalar_one_or_none()

    stt_provider = voice_settings.stt_provider if voice_settings and voice_settings.stt_provider else "openai"
    tts_provider = voice_settings.tts_provider if voice_settings and voice_settings.tts_provider else "openai"
    stt_model = voice_settings.stt_model if voice_settings else None
    tts_model = voice_settings.tts_model if voice_settings else None
    voice_id = voice_settings.voice_id if voice_settings else None
    voice_mode = voice_settings.voice_mode if voice_settings else "configured_batch"

    persona_result = await db.execute(
        select(Persona).where(
            Persona.company_id == company_id,
            Persona.is_active == True,
        )
    )
    persona = persona_result.scalar_one_or_none()

    if not persona:
        raise HTTPException(status_code=404, detail="Active persona not found")

    if session_id:
        session_result = await db.execute(
            select(ConversationSession).where(
                ConversationSession.id == session_id
            )
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.company_id != company_id:
            raise HTTPException(
                status_code=403,
                detail="Session does not belong to this company",
            )
    else:
        session = ConversationSession(
            company_id=company_id,
            persona_id=persona.id,
            channel=channel,
            status="active",
            metadata_json={
                "created_from": "configured_batch_voice_api",
                "company_name": company.name,
                "voice_mode": voice_mode,
                "stt_provider": stt_provider,
                "tts_provider": tts_provider,
            },
        )
        db.add(session)
        await db.flush()

    latency = LatencyTracker()
    latency_ms = {}

    audio_upload_info = await validate_audio_upload(audio_file)

    stt_started_at = perf_counter()

    try:
        transcript = await voice_provider_router.transcribe_audio(
            stt_provider=stt_provider,
            audio_file=audio_file,
        )
        latency.set_elapsed("stt", stt_started_at)

    except Exception as exc:
        await log_error_event(
            company_id=company_id,
            session_id=session.id if "session" in locals() else None,
            channel=channel,
            route="/voice/configured-batch",
            stage="stt",
            provider=stt_provider,
            error=exc,
            metadata={
                "filename": audio_file.filename,
                "stt_provider": stt_provider,
                "stt_model": stt_model,
            },
        )

        raise HTTPException(
            status_code=500,
            detail=build_provider_error_detail(
                stage="stt",
                provider=stt_provider,
                error=exc,
                route="/voice/configured-batch",
            ),
        )

    if not transcript:
        raise HTTPException(
            status_code=400,
            detail=f"No transcript generated using provider '{stt_provider}'",
        )

    history_result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session.id)
        .order_by(ConversationMessage.created_at.asc())
    )
    previous_messages = history_result.scalars().all()

    conversation_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in previous_messages
    ]

    user_message = ConversationMessage(
        session_id=session.id,
        role="user",
        content=transcript,
        message_type="configured_voice_transcript",
        metadata_json={
            "channel": channel,
            "filename": audio_file.filename,
            "stt_provider": stt_provider,
            "stt_model": stt_model,
            "voice_mode": voice_mode,
        },
    )
    db.add(user_message)
    await db.flush()

    await mongo_event_logger.log_event(
        company_id=company_id,
        session_id=session.id,
        channel=channel,
        event_type="configured_voice_user_transcript",
        provider=stt_provider,
        text=transcript,
        metadata={
            "filename": audio_file.filename,
            "stt_provider": stt_provider,
            "stt_model": stt_model,
            "voice_mode": voice_mode,
            "postgres_message_id": str(user_message.id),
        },
    )

    provider_used = ai_settings.llm_provider
    model_used = ai_settings.llm_model
    fallback_used = False
    fallback_attempts = []

    llm_started_at = perf_counter()

    try:
        llm_result = await llm_fallback_router.generate_text_response_with_fallback(
            primary_provider=ai_settings.llm_provider,
            primary_model=ai_settings.llm_model,
            system_prompt=ai_settings.system_prompt or "You are a helpful assistant. Keep answers short and clear.",
            user_message=transcript,
            conversation_history=conversation_history,
            temperature=ai_settings.temperature,
        )

        latency.set_elapsed("llm", llm_started_at)

        assistant_text = llm_result["text"]
        provider_used = llm_result["provider_used"]
        model_used = llm_result["model_used"]
        fallback_used = llm_result["fallback_used"]
        fallback_attempts = llm_result["attempts"]
    except Exception as exc:
        await log_error_event(
            company_id=company_id,
            session_id=session.id,
            channel=channel,
            route="/voice/configured-batch",
            stage="llm",
            provider=ai_settings.llm_provider,
            error=exc,
            metadata={
                "primary_llm_provider": ai_settings.llm_provider,
                "primary_llm_model": ai_settings.llm_model,
            },
        )

        raise HTTPException(
            status_code=500,
            detail=build_provider_error_detail(
                stage="llm",
                provider=ai_settings.llm_provider,
                error=exc,
                route="/voice/configured-batch",
            ),
        )

    tts_started_at = perf_counter()

    try:
        audio_url = await voice_provider_router.synthesize_speech(
            tts_provider=tts_provider,
            text=assistant_text,
        )
    except Exception as exc:
        await log_error_event(
            company_id=company_id,
            session_id=session.id,
            channel=channel,
            route="/voice/configured-batch",
            stage="tts",
            provider=tts_provider,
            error=exc,
            metadata={
                "tts_provider": tts_provider,
                "tts_model": tts_model,
                "voice_id": voice_id,
            },
        )

        raise HTTPException(
            status_code=500,
            detail=build_provider_error_detail(
                stage="tts",
                provider=tts_provider,
                error=exc,
                route="/voice/configured-batch",
            ),
        )

    latency.set_elapsed("tts", tts_started_at)
    latency_ms = latency.total()

    cost_estimate = estimate_voice_request_cost(
        stt_provider=stt_provider,
        llm_provider=provider_used,
        llm_model=model_used,
        tts_provider=tts_provider,
        transcript=transcript,
        assistant_text=assistant_text,
        audio_upload_info=audio_upload_info,
    )

    assistant_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        message_type="configured_voice_audio",
        metadata_json={
            "llm_provider": provider_used,
            "llm_model": model_used,
            "primary_llm_provider": ai_settings.llm_provider,
            "primary_llm_model": ai_settings.llm_model,
            "fallback_used": fallback_used,
            "fallback_attempts": fallback_attempts,
            "tts_provider": tts_provider,
            "tts_model": tts_model,
            "voice_id": voice_id,
            "audio_url": audio_url,
            "voice_mode": voice_mode,
        },
    )
    db.add(assistant_message)
    await db.flush()

    await mongo_event_logger.log_event(
        company_id=company_id,
        session_id=session.id,
        channel=channel,
        event_type="configured_voice_assistant_message",
        provider=tts_provider,
        text=assistant_text,
        metadata={
            "llm_provider": provider_used,
            "llm_model": model_used,
            "tts_provider": tts_provider,
            "tts_model": tts_model,
            "voice_id": voice_id,
            "audio_url": audio_url,
            "voice_mode": voice_mode,
            "postgres_message_id": str(assistant_message.id),
        },
    )

    await db.commit()

    return {
        "session_id": uuid_to_str(session.id),
        "company_id": uuid_to_str(company.id),
        "persona_id": uuid_to_str(persona.id),
        "transcript": transcript,
        "assistant_message": assistant_text,
        "audio_url": audio_url,
        "llm_provider": provider_used,
        "llm_model": model_used,
        "stt_provider": stt_provider,
        "stt_model": stt_model,
        "tts_provider": tts_provider,
        "tts_model": tts_model,
        "voice_id": voice_id,
        "voice_mode": voice_mode,
        "latency_ms": latency_ms,
        "cost_estimate": cost_estimate,
    }
