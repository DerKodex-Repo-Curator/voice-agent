import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

import azure.cognitiveservices.speech as speechsdk

from app.core.config import settings


class AzureSpeechVoiceService:
    def _require_config(self):
        if not settings.azure_speech_key or not settings.azure_speech_region:
            raise RuntimeError(
                "Azure Speech is missing. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env"
            )

    def _speech_config(self):
        self._require_config()

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region,
        )

        speech_config.speech_recognition_language = settings.azure_speech_language
        speech_config.speech_synthesis_voice_name = settings.azure_speech_voice_name

        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        return speech_config

    def transcribe_audio(self, audio_file) -> str:
        self._require_config()

        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)

            suffix = Path(audio_file.filename or "audio.wav").suffix or ".wav"
            input_path = temp_dir / f"input{suffix}"

            audio_file.file.seek(0)

            with input_path.open("wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)

            speech_config = self._speech_config()
            audio_config = speechsdk.audio.AudioConfig(filename=str(input_path))

            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
            )

            result = recognizer.recognize_once_async().get()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text

            if result.reason == speechsdk.ResultReason.NoMatch:
                return ""

            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.CancellationDetails(result)
                raise RuntimeError(
                    f"Azure Speech STT canceled: {cancellation.reason} {cancellation.error_details}"
                )

            return ""

    def synthesize_speech(self, text: str) -> str:
        self._require_config()

        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        output_path = generated_dir / f"{file_id}.mp3"

        speech_config = self._speech_config()
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return f"/demo/generated/{output_path.name}"

        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation = speechsdk.SpeechSynthesisCancellationDetails(result)
            raise RuntimeError(
                f"Azure Speech TTS canceled: {cancellation.reason} {cancellation.error_details}"
            )

        raise RuntimeError("Azure Speech TTS failed unexpectedly.")


azure_speech_voice_service = AzureSpeechVoiceService()
