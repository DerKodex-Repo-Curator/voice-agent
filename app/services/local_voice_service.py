import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class LocalVoiceService:
    async def save_upload_to_temp(self, audio_file: UploadFile, temp_dir: Path) -> Path:
        suffix = Path(audio_file.filename or "audio.webm").suffix or ".webm"
        input_path = temp_dir / f"input{suffix}"

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        return input_path

    def convert_to_wav_16k(self, input_path: Path, temp_dir: Path) -> Path:
        output_wav = temp_dir / "input_16k.wav"

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(output_wav),
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

        return output_wav

    def transcribe_with_whisper_cpp(self, wav_path: Path, temp_dir: Path) -> str:
        if not settings.whisper_model_path:
            raise RuntimeError("WHISPER_MODEL_PATH is missing in .env")

        model_path = Path(settings.whisper_model_path)

        if not model_path.exists():
            raise RuntimeError(f"Whisper model file not found: {model_path}")

        output_prefix = temp_dir / "transcript"

        command = [
            settings.whisper_cpp_bin,
            "-m",
            str(model_path),
            "-f",
            str(wav_path),
            "-otxt",
            "-of",
            str(output_prefix),
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            fallback_command = [
                settings.whisper_cpp_bin,
                "-m",
                str(model_path),
                "-f",
                str(wav_path),
                "--output-txt",
                "--output-file",
                str(output_prefix),
            ]

            result = subprocess.run(fallback_command, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Whisper.cpp transcription failed: {result.stderr}")

        transcript_file = Path(str(output_prefix) + ".txt")

        if transcript_file.exists():
            return transcript_file.read_text().strip()

        stdout_text = result.stdout.strip()

        if stdout_text:
            return stdout_text

        return ""

    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            input_path = await self.save_upload_to_temp(audio_file, temp_dir)
            wav_path = self.convert_to_wav_16k(input_path, temp_dir)
            transcript = self.transcribe_with_whisper_cpp(wav_path, temp_dir)

        if not transcript:
            raise RuntimeError("No transcript was generated from audio.")

        return transcript

    def synthesize_with_mac_say(self, text: str) -> str:
        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        aiff_path = generated_dir / f"{file_id}.aiff"
        wav_path = generated_dir / f"{file_id}.wav"

        say_command = [
            "say",
            "-v",
            settings.local_tts_voice,
            "-o",
            str(aiff_path),
            text,
        ]

        say_result = subprocess.run(say_command, capture_output=True, text=True)

        if say_result.returncode != 0:
            raise RuntimeError(f"macOS say TTS failed: {say_result.stderr}")

        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i",
            str(aiff_path),
            str(wav_path),
        ]

        ffmpeg_result = subprocess.run(ffmpeg_command, capture_output=True, text=True)

        if ffmpeg_result.returncode != 0:
            raise RuntimeError(f"TTS audio conversion failed: {ffmpeg_result.stderr}")

        try:
            os.remove(aiff_path)
        except OSError:
            pass

        return f"/demo/generated/{wav_path.name}"


local_voice_service = LocalVoiceService()
