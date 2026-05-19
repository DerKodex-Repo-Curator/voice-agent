import shutil
import tempfile
from pathlib import Path

from fastapi import UploadFile

from app.services.openai_voice_service import openai_voice_service
from app.services.elevenlabs_voice_service import elevenlabs_voice_service
from app.services.deepgram_voice_service import deepgram_voice_service
from app.services.aws_polly_voice_service import aws_polly_voice_service
from app.services.azure_speech_voice_service import azure_speech_voice_service
from app.services.cartesia_voice_service import cartesia_voice_service
from app.services.local_voice_service import local_voice_service


class VoiceProviderRouter:
    async def transcribe_audio(
        self,
        *,
        stt_provider: str,
        audio_file: UploadFile,
    ) -> str:
        provider = (stt_provider or "openai").lower().strip()

        audio_file.file.seek(0)

        if provider in ["openai", "openai_stt", "whisper"]:
            return await openai_voice_service.transcribe_audio(audio_file)

        if provider in ["elevenlabs", "elevenlabs_stt"]:
            return elevenlabs_voice_service.transcribe_audio(audio_file)

        if provider in ["deepgram", "deepgram_stt"]:
            return await deepgram_voice_service.transcribe_audio(audio_file)

        if provider in ["azure_speech", "azure_stt", "microsoft_speech"]:
            return azure_speech_voice_service.transcribe_audio(audio_file)

        if provider in ["whisper_cpp", "local_whisper_cpp", "local"]:
            return self._transcribe_with_local_whisper(audio_file)

        raise ValueError(f"Unsupported STT provider: {stt_provider}")

    async def synthesize_speech(
        self,
        *,
        tts_provider: str,
        text: str,
    ) -> str:
        provider = (tts_provider or "openai").lower().strip()

        if provider in ["openai", "openai_tts"]:
            return openai_voice_service.synthesize_speech(text)

        if provider in ["elevenlabs", "elevenlabs_tts"]:
            return elevenlabs_voice_service.synthesize_speech(text)

        if provider in ["deepgram", "deepgram_tts"]:
            return await deepgram_voice_service.synthesize_speech(text)

        if provider in ["aws_polly", "polly", "amazon_polly"]:
            return aws_polly_voice_service.synthesize_speech(text)

        if provider in ["azure_speech", "azure_tts", "microsoft_speech"]:
            return azure_speech_voice_service.synthesize_speech(text)

        if provider in ["cartesia", "cartesia_sonic", "sonic"]:
            return await cartesia_voice_service.synthesize_speech(text)

        if provider in ["mac_say", "local_mac_say", "local"]:
            return local_voice_service.synthesize_with_mac_say(text)

        raise ValueError(f"Unsupported TTS provider: {tts_provider}")

    def _transcribe_with_local_whisper(self, audio_file: UploadFile) -> str:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)

            suffix = Path(audio_file.filename or "audio.webm").suffix or ".webm"
            input_path = temp_dir / f"input{suffix}"

            audio_file.file.seek(0)

            with input_path.open("wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)

            wav_path = local_voice_service.convert_to_wav_16k(input_path, temp_dir)
            transcript = local_voice_service.transcribe_with_whisper_cpp(wav_path, temp_dir)

        return transcript


voice_provider_router = VoiceProviderRouter()
