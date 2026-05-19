from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
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
from app.schemas.chat_schema import ChatMessageRequest
from app.services.llm_router import llm_router
from app.services.llm_fallback_router import llm_fallback_router
from app.services.mongo_event_logger import mongo_event_logger

router = APIRouter()


def uuid_to_str(value):
    return str(value) if value is not None else None


@router.post("/message")
async def send_chat_message(
    payload: ChatMessageRequest,
    x_company_api_key: str | None = Header(default=None, alias="X-Company-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    require_company_api_key(payload.company_id, x_company_api_key)

    # 1. Check company exists
    company_result = await db.execute(
        select(Company).where(Company.id == payload.company_id)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # 2. Check text chat is enabled
    flags_result = await db.execute(
        select(CompanyFeatureFlags).where(
            CompanyFeatureFlags.company_id == payload.company_id
        )
    )
    feature_flags = flags_result.scalar_one_or_none()

    if feature_flags and not feature_flags.enable_text_chat:
        raise HTTPException(
            status_code=403,
            detail="Text chat is disabled for this company",
        )

    # 3. Load company AI settings
    ai_result = await db.execute(
        select(CompanyAISettings).where(
            CompanyAISettings.company_id == payload.company_id
        )
    )
    ai_settings = ai_result.scalar_one_or_none()

    if not ai_settings:
        raise HTTPException(
            status_code=404,
            detail="AI settings not found for this company",
        )

    # 4. Load active persona
    persona_result = await db.execute(
        select(Persona).where(
            Persona.company_id == payload.company_id,
            Persona.is_active == True,
        )
    )
    persona = persona_result.scalar_one_or_none()

    if not persona:
        raise HTTPException(
            status_code=404,
            detail="Active persona not found for this company",
        )

    # 5. Reuse existing session or create new session
    if payload.session_id:
        session_result = await db.execute(
            select(ConversationSession).where(
                ConversationSession.id == payload.session_id
            )
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.company_id != payload.company_id:
            raise HTTPException(
                status_code=403,
                detail="Session does not belong to this company",
            )
    else:
        session = ConversationSession(
            company_id=payload.company_id,
            persona_id=persona.id,
            channel=payload.channel,
            status="active",
            metadata_json={
                "created_from": "text_chat_api",
                "company_name": company.name,
            },
        )
        db.add(session)
        await db.flush()

    # 6. Load previous conversation messages
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

    # 7. Save user message
    user_message = ConversationMessage(
        session_id=session.id,
        role="user",
        content=payload.message,
        message_type="text",
        metadata_json={
            "channel": payload.channel,
        },
    )
    db.add(user_message)
    await db.flush()

    await mongo_event_logger.log_event(
        company_id=payload.company_id,
        session_id=session.id,
        channel=payload.channel,
        event_type="chat_user_message",
        provider=None,
        text=payload.message,
        metadata={
            "postgres_message_id": str(user_message.id),
            "source": "chat_message_api",
        },
    )

    # 8. Generate assistant response using selected provider
    system_prompt = (
        ai_settings.system_prompt
        or getattr(persona, "system_prompt", None)
        or "You are a helpful assistant. Keep answers short and clear."
    )

    try:
        llm_result = await llm_fallback_router.generate_text_response_with_fallback(
            primary_provider=ai_settings.llm_provider,
            primary_model=ai_settings.llm_model,
            system_prompt=system_prompt,
            user_message=payload.message,
            conversation_history=conversation_history,
            temperature=ai_settings.temperature,
        )

        assistant_text = llm_result["text"]
        provider_used = llm_result["provider_used"]
        model_used = llm_result["model_used"]
        fallback_used = llm_result["fallback_used"]
        fallback_attempts = llm_result["attempts"]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM response generation failed: {str(exc)}",
        )

    # 9. Save assistant message
    assistant_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        message_type="text",
        metadata_json={
            "model": model_used,
            "llm_provider": provider_used,
            "primary_llm_provider": ai_settings.llm_provider,
            "primary_llm_model": ai_settings.llm_model,
            "fallback_used": fallback_used,
            "fallback_attempts": fallback_attempts,
        },
    )
    db.add(assistant_message)
    await db.flush()

    await mongo_event_logger.log_event(
        company_id=payload.company_id,
        session_id=session.id,
        channel=payload.channel,
        event_type="chat_assistant_message",
        provider=provider_used,
        text=assistant_text,
        metadata={
            "model": model_used,
            "primary_llm_provider": ai_settings.llm_provider,
            "primary_llm_model": ai_settings.llm_model,
            "fallback_used": fallback_used,
            "fallback_attempts": fallback_attempts,
            "postgres_message_id": str(assistant_message.id),
            "source": "chat_message_api",
        },
    )

    await db.commit()

    return {
        "session_id": uuid_to_str(session.id),
        "company_id": uuid_to_str(company.id),
        "persona_id": uuid_to_str(persona.id),
        "user_message": payload.message,
        "assistant_message": assistant_text,
        "llm_provider": provider_used,
        "model_used": model_used,
        "primary_llm_provider": ai_settings.llm_provider,
        "primary_llm_model": ai_settings.llm_model,
        "fallback_used": fallback_used,
    }


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: UUID,
    x_company_api_key: str | None = Header(default=None, alias="X-Company-API-Key"),
    db: AsyncSession = Depends(get_db),
):
    session_result = await db.execute(
        select(ConversationSession).where(ConversationSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    require_company_api_key(session.company_id, x_company_api_key)

    messages_result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.created_at.asc())
    )
    messages = messages_result.scalars().all()

    return {
        "session_id": uuid_to_str(session.id),
        "company_id": uuid_to_str(session.company_id),
        "persona_id": uuid_to_str(session.persona_id),
        "channel": session.channel,
        "status": session.status,
        "messages": [
            {
                "id": uuid_to_str(message.id),
                "role": message.role,
                "content": message.content,
                "message_type": message.message_type,
                "created_at": message.created_at,
                "metadata": message.metadata_json,
            }
            for message in messages
        ],
    }
