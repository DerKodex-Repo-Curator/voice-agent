import json
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

router = APIRouter()


def uuid_to_str(value):
    return str(value) if value is not None else None


async def process_streamed_audio(
    company_id: UUID,
    session_id: UUID | None,
    channel: str,
    audio_chunks: list[bytes],
    db: AsyncSession,
):
    company_result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        raise ValueError("Company not found")

    flags_result = await db.execute(
        select(CompanyFeatureFlags).where(
            CompanyFeatureFlags.company_id == company_id
        )
    )
    feature_flags = flags_result.scalar_one_or_none()

    if feature_flags and not feature_flags.enable_voice_chat:
        raise ValueError("Voice chat is disabled for this company")

    ai_result = await db.execute(
        select(CompanyAISettings).where(
            CompanyAISettings.company_id == company_id
        )
    )
    ai_settings = ai_result.scalar_one_or_none()

    if not ai_settings:
        raise ValueError("AI settings not found")

    persona_result = await db.execute(
        select(Persona).where(
            Persona.company_id == company_id,
            Persona.is_active == True,
        )
    )
    persona = persona_result.scalar_one_or_none()

    if not persona:
        raise ValueError("Active persona not found")

    if session_id:
        session_result = await db.execute(
            select(ConversationSession).where(
                ConversationSession.id == session_id
            )
        )
        session = session_result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        if session.company_id != company_id:
            raise ValueError("Session does not belong to this company")
    else:
        session = ConversationSession(
            company_id=company_id,
            persona_id=persona.id,
            channel=channel,
            status="active",
            metadata_json={
                "created_from": "websocket_voice_stream",
                "company_name": company.name,
            },
        )
        db.add(session)
        await db.flush()

    await db.flush()

    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        input_path = temp_dir / "stream_input.webm"

        with input_path.open("wb") as file:
            for chunk in audio_chunks:
                file.write(chunk)

        wav_path = local_voice_service.convert_to_wav_16k(input_path, temp_dir)
        transcript = local_voice_service.transcribe_with_whisper_cpp(wav_path, temp_dir)

    if not transcript:
        raise ValueError("No transcript generated from streamed audio")

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
        message_type="websocket_audio_transcript",
        metadata_json={
            "channel": channel,
            "stt_provider": "local_whisper_cpp",
            "transport": "websocket_audio_chunks",
        },
    )
    db.add(user_message)
    await db.flush()

    assistant_text = await llm_router.generate_text_response(
        provider=ai_settings.llm_provider,
        model=ai_settings.llm_model,
        system_prompt=ai_settings.system_prompt,
        user_message=transcript,
        conversation_history=conversation_history,
        temperature=ai_settings.temperature,
    )

    audio_url = local_voice_service.synthesize_with_mac_say(assistant_text)

    assistant_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_text,
        message_type="websocket_local_tts_audio",
        metadata_json={
            "llm_provider": ai_settings.llm_provider,
            "model": ai_settings.llm_model,
            "tts_provider": "mac_say",
            "audio_url": audio_url,
            "transport": "websocket_audio_chunks",
        },
    )
    db.add(assistant_message)

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


@router.websocket("/voice-stream")
async def voice_stream_websocket(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    await websocket.accept()

    audio_chunks: list[bytes] = []
    company_id: UUID | None = None
    session_id: UUID | None = None
    channel = "websocket_voice_stream"

    try:
        while True:
            message = await websocket.receive()

            if message.get("text"):
                data = json.loads(message["text"])
                event_type = data.get("type")

                if event_type == "start":
                    company_id = UUID(data["company_id"])

                    raw_session_id = data.get("session_id")
                    session_id = UUID(raw_session_id) if raw_session_id else None

                    channel = data.get("channel", "websocket_voice_stream")
                    audio_chunks = []

                    await websocket.send_json({
                        "type": "ready",
                        "message": "WebSocket voice stream started",
                    })

                elif event_type == "stop":
                    if not company_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "company_id was not provided",
                        })
                        continue

                    if not audio_chunks:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio chunks received",
                        })
                        continue

                    await websocket.send_json({
                        "type": "processing",
                        "message": "Processing audio with local Whisper and LLM",
                        "chunks_received": len(audio_chunks),
                    })

                    try:
                        result = await process_streamed_audio(
                            company_id=company_id,
                            session_id=session_id,
                            channel=channel,
                            audio_chunks=audio_chunks,
                            db=db,
                        )

                        await websocket.send_json({
                            "type": "final",
                            **result,
                        })

                    except Exception as exc:
                        await websocket.send_json({
                            "type": "error",
                            "message": str(exc),
                        })

                    break

            elif message.get("bytes"):
                audio_chunks.append(message["bytes"])

                if len(audio_chunks) % 5 == 0:
                    await websocket.send_json({
                        "type": "chunk_ack",
                        "chunks_received": len(audio_chunks),
                    })

    except WebSocketDisconnect:
        return
