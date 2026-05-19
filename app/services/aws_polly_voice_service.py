from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class AWSPollyVoiceService:
    def __init__(self):
        self.client = boto3.client(
            "polly",
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def synthesize_speech(self, text: str) -> str:
        generated_dir = Path("app/static/generated")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        output_path = generated_dir / f"{file_id}.mp3"

        try:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat=settings.aws_polly_output_format,
                VoiceId=settings.aws_polly_voice_id,
                Engine=settings.aws_polly_engine,
            )
        except ClientError:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat=settings.aws_polly_output_format,
                VoiceId=settings.aws_polly_voice_id,
                Engine="standard",
            )

        audio_stream = response.get("AudioStream")

        if not audio_stream:
            raise RuntimeError("AWS Polly did not return an audio stream.")

        output_path.write_bytes(audio_stream.read())

        return f"/demo/generated/{output_path.name}"


aws_polly_voice_service = AWSPollyVoiceService()
