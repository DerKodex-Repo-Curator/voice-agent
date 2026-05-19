import json
from fastapi import HTTPException


def extract_error_message(error: Exception | str) -> str:
    if isinstance(error, str):
        return error

    if isinstance(error, HTTPException):
        detail = error.detail

        if isinstance(detail, (dict, list)):
            return json.dumps(detail)

        if detail:
            return str(detail)

    message = str(error)

    if message:
        return message

    return repr(error)


def provider_suggestion(stage: str, provider: str) -> str | None:
    provider = (provider or "").lower()
    stage = (stage or "").lower()

    if stage == "tts" and provider == "cartesia":
        return "Check CARTESIA_API_KEY, CARTESIA_VOICE_ID UUID, CARTESIA_MODEL_ID, and Cartesia-Version in .env."

    if stage == "tts" and provider == "azure_speech":
        return "Check AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, and voice name such as en-US-JennyNeural."

    if stage == "tts" and provider == "aws_polly":
        return "Check AWS credentials, AWS_DEFAULT_REGION, AWS_POLLY_VOICE_ID, and Polly permissions."

    if stage == "stt" and provider == "deepgram":
        return "Check DEEPGRAM_API_KEY, STT model nova-3, and audio file type/format."

    if stage == "llm" and provider == "bedrock":
        return "Check AWS Bedrock credentials, model access, region, and AWS_BEDROCK_MODEL_ID."

    if stage == "llm" and provider == "azure_openai":
        return "Check Azure OpenAI quota/deployment, AZURE_OPENAI_ENDPOINT, API key, API version, and deployment name."

    return None


def build_provider_error_detail(
    *,
    stage: str,
    provider: str,
    error: Exception | str,
    route: str | None = None,
):
    detail = {
        "stage": stage,
        "provider": provider,
        "message": extract_error_message(error),
    }

    suggestion = provider_suggestion(stage, provider)

    if suggestion:
        detail["suggestion"] = suggestion

    if route:
        detail["route"] = route

    return detail
