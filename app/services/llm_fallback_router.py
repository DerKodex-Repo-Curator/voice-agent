from app.core.config import settings
from app.services.llm_router import llm_router


def is_present(value) -> bool:
    if not value:
        return False

    lowered = str(value).strip().lower()

    if not lowered:
        return False

    invalid_words = ["your_", "paste_", "replace_", "here", "string"]

    return not any(word in lowered for word in invalid_words)


class LLMFallbackRouter:
    def _configured_fallbacks(self):
        fallbacks = []

        if is_present(getattr(settings, "openrouter_api_key", None)):
            fallbacks.append(
                {
                    "provider": "openrouter",
                    "model": getattr(settings, "openrouter_model", "openrouter/free"),
                }
            )

        # Ollama is local. It works only if Ollama is running.
        fallbacks.append(
            {
                "provider": "ollama",
                "model": getattr(settings, "ollama_model_id", "llama3.2:1b"),
            }
        )

        if is_present(getattr(settings, "anthropic_api_key", None)):
            fallbacks.append(
                {
                    "provider": "anthropic",
                    "model": getattr(settings, "anthropic_model_id", "claude-sonnet-4-6"),
                }
            )

        if is_present(getattr(settings, "gemini_api_key", None)) or is_present(getattr(settings, "google_api_key", None)):
            fallbacks.append(
                {
                    "provider": "gemini",
                    "model": getattr(settings, "gemini_model_id", "gemini-2.5-flash"),
                }
            )

        if is_present(getattr(settings, "aws_access_key_id", None)) and is_present(getattr(settings, "aws_bedrock_model_id", None)):
            fallbacks.append(
                {
                    "provider": "bedrock",
                    "model": getattr(settings, "aws_bedrock_model_id", None),
                }
            )

        if is_present(getattr(settings, "hf_token", None)) or is_present(getattr(settings, "huggingface_api_key", None)):
            fallbacks.append(
                {
                    "provider": "huggingface",
                    "model": getattr(settings, "huggingface_model_id", "meta-llama/Llama-3.1-8B-Instruct"),
                }
            )

        if is_present(getattr(settings, "openai_api_key", None)):
            fallbacks.append(
                {
                    "provider": "openai",
                    "model": getattr(settings, "openai_model", "gpt-4o-mini"),
                }
            )

        return fallbacks

    async def generate_text_response_with_fallback(
        self,
        *,
        primary_provider: str,
        primary_model: str | None,
        system_prompt: str | None,
        user_message: str,
        conversation_history: list[dict] | None = None,
        temperature: float = 0.7,
    ):
        attempts = []

        candidates = [
            {
                "provider": primary_provider,
                "model": primary_model,
                "type": "primary",
            }
        ]

        for fallback in self._configured_fallbacks():
            if fallback["provider"] != primary_provider:
                candidates.append(
                    {
                        "provider": fallback["provider"],
                        "model": fallback["model"],
                        "type": "fallback",
                    }
                )

        last_error = None

        for candidate in candidates:
            provider = candidate["provider"]
            model = candidate["model"]

            try:
                text = await llm_router.generate_text_response(
                    provider=provider,
                    model=model,
                    system_prompt=system_prompt,
                    user_message=user_message,
                    conversation_history=conversation_history or [],
                    temperature=temperature,
                )

                attempts.append(
                    {
                        "provider": provider,
                        "model": model,
                        "status": "success",
                        "type": candidate["type"],
                    }
                )

                return {
                    "text": text,
                    "provider_used": provider,
                    "model_used": model,
                    "fallback_used": candidate["type"] == "fallback",
                    "attempts": attempts,
                }

            except Exception as exc:
                last_error = str(exc)
                attempts.append(
                    {
                        "provider": provider,
                        "model": model,
                        "status": "failed",
                        "type": candidate["type"],
                        "error": str(exc)[:500],
                    }
                )

        raise RuntimeError(
            {
                "message": "All LLM providers failed",
                "last_error": last_error,
                "attempts": attempts,
            }
        )


llm_fallback_router = LLMFallbackRouter()
