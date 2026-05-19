from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


def is_present(value: str | None, placeholder_words: list[str] | None = None) -> bool:
    if not value:
        return False

    cleaned = value.strip()

    if not cleaned:
        return False

    placeholders = placeholder_words or [
        "your_",
        "paste_",
        "replace_",
        "here",
    ]

    lowered = cleaned.lower()

    return not any(word in lowered for word in placeholders)


def status_configured(condition: bool, fallback: str = "not_configured") -> str:
    return "configured" if condition else fallback


@router.get("/status")
async def provider_status():
    llm_providers = {
        "openai": status_configured(is_present(settings.openai_api_key)),
        "openrouter": status_configured(is_present(settings.openrouter_api_key)),
        "huggingface": status_configured(
            is_present(settings.hf_token) or is_present(settings.huggingface_api_key)
        ),
        "anthropic": status_configured(is_present(settings.anthropic_api_key)),
        "gemini": status_configured(
            is_present(settings.gemini_api_key) or is_present(settings.google_api_key)
        ),
        "bedrock": status_configured(
            is_present(settings.aws_access_key_id)
            and is_present(settings.aws_secret_access_key)
            and is_present(settings.aws_bedrock_model_id)
        ),
        "ollama": "local_configured",
        "azure_openai": (
            "configured"
            if (
                is_present(settings.azure_openai_api_key)
                and is_present(settings.azure_openai_endpoint)
                and is_present(settings.azure_openai_deployment_name)
            )
            else "pending_quota_or_deployment"
        ),
    }

    stt_providers = {
        "openai": status_configured(is_present(settings.openai_api_key)),
        "elevenlabs": status_configured(is_present(settings.elevenlabs_api_key)),
        "deepgram": status_configured(is_present(settings.deepgram_api_key)),
        "azure_speech": status_configured(
            is_present(settings.azure_speech_key)
            and is_present(settings.azure_speech_region)
        ),
        "whisper_cpp": "local_configured",
    }

    tts_providers = {
        "openai": status_configured(is_present(settings.openai_api_key)),
        "elevenlabs": status_configured(is_present(settings.elevenlabs_api_key)),
        "deepgram": status_configured(is_present(settings.deepgram_api_key)),
        "aws_polly": status_configured(
            is_present(settings.aws_access_key_id)
            and is_present(settings.aws_secret_access_key)
        ),
        "azure_speech": status_configured(
            is_present(settings.azure_speech_key)
            and is_present(settings.azure_speech_region)
        ),
        "cartesia": status_configured(
            is_present(getattr(settings, "cartesia_api_key", None))
            and is_present(getattr(settings, "cartesia_voice_id", None))
        ),
        "mac_say": "local_configured",
    }

    realtime_providers = {
        "openai_realtime": status_configured(is_present(settings.openai_api_key)),
        "twilio_media_streams": status_configured(
            is_present(settings.twilio_auth_token)
            and is_present(settings.twilio_webhook_base_url)
        ),
    }

    return {
        "status": "ok",
        "llm_providers": llm_providers,
        "stt_providers": stt_providers,
        "tts_providers": tts_providers,
        "realtime_providers": realtime_providers,
        "notes": {
            "azure_openai": "Azure OpenAI LLM is pending quota/deployment if status is pending_quota_or_deployment.",
            "ollama": "Ollama is local and requires ollama running on the machine.",
            "local_providers": "Local providers do not require cloud API keys.",
        },
    }
