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
    ConversationMessage,
    ConversationSession,
    Persona,
)
from app.services.llm_router import llm_router
from app.services.local_voice_service import local_voice_service
from app.services.mongo_event_logger import mongo_event_logger

router = APIRouter()


def uuid_to_str(value):
    return str(value) if value is not None else None


@router.post("/local-chat", include_in_schema=False)
async def local_voice_chat(
    company_id: UUID = Form(...),
    session_id: UUID | None = Form(default=None),
    channel: str = Form(default="backend_local_voice"),
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
                "created_from": "local_backend_voice_api",
                "company_name": company.name,
            },
        )
        db.add(session)
        await db.flush()

    try:
        transcript = await local_voice_service.transcribe_audio(audio_file)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Local transcription failed: {str(exc)}",
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
        message_type="audio_transcript",
        metadata_json={
            "channel": channel,
            "filename": audio_file.filename,
            "stt_provider": "local_whisper_cpp",
        },
    )
    db.add(user_message)
    await db.flush()

    try:
        assistant_text = await llm_router.generate_text_response(
            provider=ai_settings.llm_provider,
            model=ai_settings.llm_model,
            system_prompt=ai_settings.system_prompt,
            user_message=transcript,
            conversation_history=conversation_history,
            temperature=ai_settings.temperature,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM response generation failed: {str(exc)}",
        )

    try:
        audio_url = local_voice_service.synthesize_with_mac_say(assistant_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Local TTS failed: {str(exc)}",
        )

    assistant_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        message_type="local_tts_audio",
        metadata_json={
            "llm_provider": ai_settings.llm_provider,
            "model": ai_settings.llm_model,
            "tts_provider": "mac_say",
            "audio_url": audio_url,
        },
    )
    db.add(assistant_message)

    await mongo_event_logger.log_event(
        company_id=company_id,
        session_id=session.id,
        channel=channel,
        event_type="voice_assistant_message",
        provider=ai_settings.llm_provider,
        text=assistant_text,
        metadata={
            "source": "local_voice",
            "llm_model": ai_settings.llm_model,
            "tts_provider": "mac_say",
            "audio_url": audio_url,
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
        "llm_provider": ai_settings.llm_provider,
        "model_used": ai_settings.llm_model,
        "stt_provider": "local_whisper_cpp",
        "tts_provider": "mac_say",
    }
