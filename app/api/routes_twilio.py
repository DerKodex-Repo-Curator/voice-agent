from uuid import UUID
from urllib.parse import urlencode
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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
from app.services.openai_voice_service import openai_voice_service
from app.services.mongo_event_logger import mongo_event_logger

router = APIRouter()


def xml_response(xml: str):
    return Response(content=xml, media_type="application/xml")


def get_base_url(request: Request) -> str:
    if settings.twilio_webhook_base_url:
        return settings.twilio_webhook_base_url.rstrip("/")

    return str(request.base_url).rstrip("/")


def build_url(base_url: str, path: str, params: dict | None = None) -> str:
    clean_params = {}

    if params:
        clean_params = {
            key: value
            for key, value in params.items()
            if value is not None and value != ""
        }

    url = f"{base_url}{path}"

    if clean_params:
        return f"{url}?{urlencode(clean_params)}"

    return url


def uuid_to_str(value):
    return str(value) if value is not None else None


async def load_company_context(company_id: UUID, db: AsyncSession):
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

    if feature_flags and not feature_flags.enable_phone_calling:
        raise HTTPException(
            status_code=403,
            detail="Phone calling is disabled for this company",
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

    return company, feature_flags, ai_settings, persona


async def get_or_create_call_session(
    company_id: UUID,
    session_id: UUID | None,
    call_sid: str | None,
    company_name: str,
    persona_id: UUID,
    db: AsyncSession,
):
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

        return session

    session = ConversationSession(
        company_id=company_id,
        persona_id=persona_id,
        channel="twilio_phone_batch",
        status="active",
        metadata_json={
            "created_from": "twilio_phone_call",
            "company_name": company_name,
            "call_sid": call_sid,
        },
    )

    db.add(session)
    await db.flush()

    return session


@router.post("/voice")
async def twilio_voice_entry(
    request: Request,
    company_id: UUID,
    session_id: UUID | None = None,
):
    base_url = get_base_url(request)

    await mongo_event_logger.log_event(
        company_id=company_id,
        session_id=session_id,
        channel="twilio_phone_batch",
        event_type="twilio_voice_prompt",
        provider="twilio",
        text="Twilio voice prompt started",
        metadata={
            "source": "twilio_voice_entry",
        },
    )

    gather_action = build_url(
        base_url,
        "/twilio/respond",
        {
            "company_id": str(company_id),
            "session_id": str(session_id) if session_id else None,
        },
    )

    retry_url = build_url(
        base_url,
        "/twilio/voice",
        {
            "company_id": str(company_id),
            "session_id": str(session_id) if session_id else None,
        },
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="{escape(gather_action)}" method="POST" speechTimeout="auto" timeout="5">
        <Say voice="alice">Hi. You are connected to the AI voice assistant. Please speak after the beep.</Say>
    </Gather>
    <Say voice="alice">I did not hear anything. Let us try again.</Say>
    <Redirect method="POST">{escape(retry_url)}</Redirect>
</Response>
"""

    return xml_response(xml)


@router.post("/respond")
async def twilio_respond(
    request: Request,
    company_id: UUID,
    session_id: UUID | None = None,
    SpeechResult: str = Form(default=""),
    CallSid: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
):
    base_url = get_base_url(request)

    if not SpeechResult.strip():
        retry_url = build_url(
            base_url,
            "/twilio/voice",
            {
                "company_id": str(company_id),
                "session_id": str(session_id) if session_id else None,
            },
        )

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Sorry, I could not understand that.</Say>
    <Redirect method="POST">{escape(retry_url)}</Redirect>
</Response>
"""
        return xml_response(xml)

    company, feature_flags, ai_settings, persona = await load_company_context(
        company_id=company_id,
        db=db,
    )

    session = await get_or_create_call_session(
        company_id=company_id,
        session_id=session_id,
        call_sid=CallSid,
        company_name=company.name,
        persona_id=persona.id,
        db=db,
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
        content=SpeechResult.strip(),
        message_type="twilio_speech_result",
        metadata_json={
            "channel": "twilio_phone_batch",
            "call_sid": CallSid,
            "stt_provider": "twilio_gather",
        },
    )
    db.add(user_message)
    await db.flush()

    await mongo_event_logger.log_event(
        company_id=company_id,
        session_id=session.id,
        channel="twilio_phone_batch",
        event_type="twilio_user_speech",
        provider="twilio_gather",
        text=SpeechResult.strip(),
        metadata={
            "call_sid": CallSid,
            "postgres_message_id": str(user_message.id),
            "source": "twilio_respond",
        },
    )

    try:
        assistant_text = await llm_router.generate_text_response(
            provider=ai_settings.llm_provider,
            model=ai_settings.llm_model,
            system_prompt=ai_settings.system_prompt,
            user_message=SpeechResult.strip(),
            conversation_history=conversation_history,
            temperature=ai_settings.temperature,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM response generation failed: {str(exc)}",
        )

    try:
        audio_url = openai_voice_service.synthesize_speech(assistant_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI TTS failed: {str(exc)}",
        )

    assistant_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        message_type="twilio_openai_tts_audio",
        metadata_json={
            "channel": "twilio_phone_batch",
            "call_sid": CallSid,
            "llm_provider": ai_settings.llm_provider,
            "model": ai_settings.llm_model,
            "tts_provider": "openai",
            "audio_url": audio_url,
        },
    )
    db.add(assistant_message)
    await db.flush()

    await mongo_event_logger.log_event(
        company_id=company_id,
        session_id=session.id,
        channel="twilio_phone_batch",
        event_type="twilio_assistant_response",
        provider=ai_settings.llm_provider,
        text=assistant_text,
        metadata={
            "call_sid": CallSid,
            "llm_model": ai_settings.llm_model,
            "tts_provider": "openai",
            "audio_url": audio_url,
            "postgres_message_id": str(assistant_message.id),
            "source": "twilio_respond",
        },
    )

    await db.commit()

    public_audio_url = f"{base_url}{audio_url}"

    next_url = build_url(
        base_url,
        "/twilio/voice",
        {
            "company_id": str(company_id),
            "session_id": str(session.id),
        },
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{escape(public_audio_url)}</Play>
    <Redirect method="POST">{escape(next_url)}</Redirect>
</Response>
"""

    return xml_response(xml)
