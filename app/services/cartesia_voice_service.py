from pathlib import Path
from uuid import uuid4

import httpx

from app.core.config import settings


class CartesiaVoiceService:
    async def synthesize_speech(self, text: str) -> str:
        if not settings.cartesia_api_key:
            raise RuntimeError("CARTESIA_API_KEY is missing in .env")

        if not settings.cartesia_voice_id:
            raise RuntimeError("CARTESIA_VOICE_ID is missing in .env")

        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        output_path = generated_dir / f"{file_id}.mp3"

        payload = {
            "model_id": settings.cartesia_model_id,
            "transcript": text,
            "voice": {
                "mode": "id",
                "id": settings.cartesia_voice_id,
            },
            "output_format": {
                "container": "mp3",
                "sample_rate": 44100,
                "bit_rate": 128000,
            },
            "language": settings.cartesia_language,
        }

        headers = {
            "Authorization": f"Bearer {settings.cartesia_api_key}",
            "Cartesia-Version": settings.cartesia_version,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.cartesia.ai/tts/bytes",
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"Cartesia TTS failed: {response.status_code} {response.text}"
            )

        output_path.write_bytes(response.content)

        return f"/demo/generated/{output_path.name}"


cartesia_voice_service = CartesiaVoiceService()
