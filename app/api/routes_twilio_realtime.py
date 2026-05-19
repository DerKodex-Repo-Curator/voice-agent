import asyncio
import json
import ssl
from uuid import UUID
from xml.sax.saxutils import escape

import certifi
import websockets
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from app.core.config import settings
from app.core.security import require_twilio_signature
from app.services.mongo_event_logger import mongo_event_logger

router = APIRouter()


def xml_response(xml: str):
    return Response(content=xml, media_type="application/xml")


def get_base_url(request: Request) -> str:
    if settings.twilio_webhook_base_url:
        return settings.twilio_webhook_base_url.rstrip("/")
    return str(request.base_url).rstrip("/")


def https_to_wss(url: str) -> str:
    if url.startswith("https://"):
        return "wss://" + url.removeprefix("https://")
    if url.startswith("http://"):
        return "ws://" + url.removeprefix("http://")
    return url


@router.post("/stream-twiml", dependencies=[Depends(require_twilio_signature)])
async def twilio_realtime_stream_twiml(
    request: Request,
    company_id: UUID,
):
    base_url = get_base_url(request)
    websocket_base = https_to_wss(base_url)

    # IMPORTANT:
    # Twilio <Stream> URL must NOT contain query params.
    # We pass company_id using <Parameter> instead.
    stream_url = f"{websocket_base}/twilio-realtime/media-stream"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{escape(stream_url)}">
            <Parameter name="company_id" value="{escape(str(company_id))}" />
        </Stream>
    </Connect>
</Response>
"""

    return xml_response(xml)


async def connect_to_openai_realtime():
    if (
        not settings.openai_api_key
        or settings.openai_api_key == "your_openai_api_key_here"
    ):
        raise RuntimeError("OPENAI_API_KEY is missing in .env")

    url = f"wss://api.openai.com/v1/realtime?model={settings.realtime_model}"

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "OpenAI-Beta": "realtime=v1",
    }

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        return await websockets.connect(
            url,
            additional_headers=headers,
            ssl=ssl_context,
            ping_interval=20,
            ping_timeout=20,
        )
    except TypeError:
        return await websockets.connect(
            url,
            extra_headers=headers,
            ssl=ssl_context,
            ping_interval=20,
            ping_timeout=20,
        )


async def configure_openai_session(openai_ws):
    session_update = {
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "instructions": (
                "You are a helpful phone voice assistant. "
                "Always respond only in clear English. "
                "Do not switch languages. "
                "Even if the caller has an accent or says mixed-language words, reply in English only. "
                "Keep responses short, natural, and conversational. "
                "Do not mention internal systems."
            ),
            "voice": settings.realtime_voice,
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 700
            },
            "temperature": 0.8
        }
    }

    await openai_ws.send(json.dumps(session_update))


@router.websocket("/media-stream")
async def twilio_realtime_media_stream(websocket: WebSocket):
    await websocket.accept()

    stream_sid = None
    company_id = None
    openai_ws = None

    try:
        openai_ws = await connect_to_openai_realtime()
        await configure_openai_session(openai_ws)

        async def receive_from_twilio():
            nonlocal stream_sid, company_id

            try:
                while True:
                    message_text = await websocket.receive_text()
                    data = json.loads(message_text)

                    event_type = data.get("event")

                    if event_type == "start":
                        start_data = data.get("start", {})
                        stream_sid = start_data.get("streamSid")

                        custom_params = start_data.get("customParameters", {})
                        company_id = custom_params.get("company_id")

                        print(f"Twilio stream started: {stream_sid}")
                        print(f"Company ID from Twilio parameter: {company_id}")

                        await mongo_event_logger.log_event(
                            company_id=company_id,
                            session_id=stream_sid,
                            channel="twilio_realtime",
                            event_type="twilio_realtime_stream_started",
                            provider="twilio_media_streams",
                            text="Twilio realtime media stream started",
                            metadata={
                                "stream_sid": stream_sid,
                                "source": "twilio_realtime_media_stream",
                            },
                        )

                    elif event_type == "media":
                        media_payload = data.get("media", {}).get("payload")

                        if media_payload:
                            await openai_ws.send(
                                json.dumps(
                                    {
                                        "type": "input_audio_buffer.append",
                                        "audio": media_payload,
                                    }
                                )
                            )

                    elif event_type == "stop":
                        print("Twilio stream stopped")

                        await mongo_event_logger.log_event(
                            company_id=company_id,
                            session_id=stream_sid,
                            channel="twilio_realtime",
                            event_type="twilio_realtime_stream_stopped",
                            provider="twilio_media_streams",
                            text="Twilio realtime media stream stopped",
                            metadata={
                                "stream_sid": stream_sid,
                                "source": "twilio_realtime_media_stream",
                            },
                        )

                        await openai_ws.close()
                        break

            except WebSocketDisconnect:
                print("Twilio WebSocket disconnected")
                if openai_ws:
                    await openai_ws.close()

        async def receive_from_openai():
            nonlocal stream_sid

            try:
                async for openai_message in openai_ws:
                    event = json.loads(openai_message)
                    event_type = event.get("type")

                    if event_type in [
                        "response.audio.delta",
                        "response.output_audio.delta",
                    ]:
                        audio_delta = event.get("delta")

                        if audio_delta and stream_sid:
                            await websocket.send_json(
                                {
                                    "event": "media",
                                    "streamSid": stream_sid,
                                    "media": {
                                        "payload": audio_delta,
                                    },
                                }
                            )

                    elif event_type == "input_audio_buffer.speech_started":
                        if stream_sid:
                            await websocket.send_json(
                                {
                                    "event": "clear",
                                    "streamSid": stream_sid,
                                }
                            )

                    elif event_type == "error":
                        print("OpenAI realtime error:", event)

                        await mongo_event_logger.log_event(
                            company_id=company_id,
                            session_id=stream_sid,
                            channel="twilio_realtime",
                            event_type="openai_realtime_error",
                            provider="openai_realtime",
                            text="OpenAI realtime error",
                            metadata={
                                "stream_sid": stream_sid,
                                "error": event,
                                "source": "twilio_realtime_media_stream",
                            },
                        )

                    elif event_type in [
                        "response.done",
                        "conversation.item.input_audio_transcription.completed",
                    ]:
                        print("OpenAI event:", event_type)

            except Exception as exc:
                print(f"OpenAI receive loop error: {exc}")

        await asyncio.gather(
            receive_from_twilio(),
            receive_from_openai(),
        )

    except Exception as exc:
        print(f"Twilio realtime bridge error: {exc}")

        try:
            await websocket.close()
        except Exception:
            pass

    finally:
        if openai_ws:
            try:
                await openai_ws.close()
            except Exception:
                pass
