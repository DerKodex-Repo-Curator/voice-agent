from pathlib import Path
from uuid import uuid4

from elevenlabs.client import ElevenLabs

from app.core.config import settings


class ElevenLabsVoiceService:
    def __init__(self):
        if (
            not settings.elevenlabs_api_key
            or settings.elevenlabs_api_key == "your_elevenlabs_api_key_here"
        ):
            self.client = None
        else:
            self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    def _require_client(self):
        if self.client is None:
            raise RuntimeError(
                "ElevenLabs API key is missing. Please update ELEVENLABS_API_KEY in .env"
            )

    def transcribe_audio(self, audio_file) -> str:
        self._require_client()

        audio_file.file.seek(0)

        result = self.client.speech_to_text.convert(
            file=audio_file.file,
            model_id=settings.elevenlabs_stt_model_id,
        )

        if hasattr(result, "text"):
            return result.text

        if isinstance(result, dict):
            return result.get("text", "")

        return str(result)

    def synthesize_speech(self, text: str) -> str:
        self._require_client()

        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        output_path = generated_dir / f"{file_id}.mp3"

        audio_stream = self.client.text_to_speech.convert(
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model_id,
            output_format=settings.elevenlabs_output_format,
            text=text,
        )

        with output_path.open("wb") as audio_file:
            for chunk in audio_stream:
                if chunk:
                    audio_file.write(chunk)

        return f"/demo/generated/{output_path.name}"


elevenlabs_voice_service = ElevenLabsVoiceService()
