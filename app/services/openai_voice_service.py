import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from openai import OpenAI

from app.core.config import settings


class OpenAIVoiceService:
    def __init__(self):
        if (
            not settings.openai_api_key
            or settings.openai_api_key == "your_openai_api_key_here"
        ):
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)

    def _require_client(self):
        if self.client is None:
            raise RuntimeError("OpenAI API key is missing. Please update OPENAI_API_KEY in .env")

    async def save_upload_to_temp(self, audio_file: UploadFile, temp_dir: Path) -> Path:
        suffix = Path(audio_file.filename or "audio.webm").suffix or ".webm"
        input_path = temp_dir / f"input{suffix}"

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        return input_path

    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        self._require_client()

        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            input_path = await self.save_upload_to_temp(audio_file, temp_dir)

            with input_path.open("rb") as file_obj:
                transcription = self.client.audio.transcriptions.create(
                    model=settings.openai_stt_model,
                    file=file_obj,
                )

        transcript = getattr(transcription, "text", None)

        if not transcript:
            raise RuntimeError("OpenAI transcription returned empty text.")

        return transcript.strip()

    def synthesize_speech(self, text: str) -> str:
        self._require_client()

        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        output_path = generated_dir / f"{file_id}.{settings.openai_tts_format}"

        with self.client.audio.speech.with_streaming_response.create(
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,
            input=text,
            response_format=settings.openai_tts_format,
        ) as response:
            response.stream_to_file(output_path)

        return f"/demo/generated/{output_path.name}"


openai_voice_service = OpenAIVoiceService()
