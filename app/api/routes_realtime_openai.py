import json

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings

router = APIRouter()


@router.post("/session", response_class=PlainTextResponse)
async def create_realtime_session(request: Request, sdp: str = Body(..., media_type="application/sdp")):
    if (
        not settings.openai_api_key
        or settings.openai_api_key == "your_openai_api_key_here"
    ):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is missing in .env",
        )

    session_config = {
        "type": "realtime",
        "model": settings.realtime_model,
        "instructions": (
            "You are a helpful, concise voice assistant. "
            "Keep responses short, natural, and conversational."
        ),
        "audio": {
            "output": {
                "voice": settings.realtime_voice
            }
        }
    }

    files = {
        "sdp": (None, sdp, "application/sdp"),
        "session": (None, json.dumps(session_config), "application/json"),
    }

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/calls",
                headers=headers,
                files=files,
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text,
            )

        return PlainTextResponse(
            content=response.text,
            media_type="application/sdp",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Realtime session creation failed: {str(exc)}",
        )
