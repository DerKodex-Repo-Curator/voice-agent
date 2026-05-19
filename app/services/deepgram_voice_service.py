from pathlib import Path
from uuid import uuid4

import httpx

from app.core.config import settings


class DeepgramVoiceService:
    def _require_key(self):
        if (
            not settings.deepgram_api_key
            or settings.deepgram_api_key == "your_deepgram_api_key_here"
        ):
            raise RuntimeError("DEEPGRAM_API_KEY is missing in .env")

    async def transcribe_audio(self, audio_file) -> str:
        self._require_key()

        audio_bytes = await audio_file.read()
        content_type = audio_file.content_type or "application/octet-stream"

        params = {
            "model": settings.deepgram_stt_model,
            "smart_format": "true",
            "punctuate": "true",
            "language": settings.deepgram_language,
        }

        headers = {
            "Authorization": f"Token {settings.deepgram_api_key}",
            "Content-Type": content_type,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                params=params,
                headers=headers,
                content=audio_bytes,
            )

        if response.status_code >= 400:
            raise RuntimeError(f"Deepgram STT failed: {response.status_code} {response.text}")

        data = response.json()

        try:
            transcript = (
                data["results"]["channels"][0]["alternatives"][0]["transcript"]
            )
        except Exception:
            transcript = ""

        return transcript

    async def synthesize_speech(self, text: str) -> str:
        self._require_key()

        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        output_path = generated_dir / f"{file_id}.mp3"

        headers = {
            "Authorization": f"Token {settings.deepgram_api_key}",
            "Content-Type": "application/json",
        }

        params = {
            "model": settings.deepgram_tts_model,
        }

        payload = {
            "text": text,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/speak",
                params=params,
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise RuntimeError(f"Deepgram TTS failed: {response.status_code} {response.text}")

        output_path.write_bytes(response.content)

        return f"/demo/generated/{output_path.name}"


deepgram_voice_service = DeepgramVoiceService()
