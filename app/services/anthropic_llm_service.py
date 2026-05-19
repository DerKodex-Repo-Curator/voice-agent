import asyncio

import anthropic

from app.core.config import settings


class AnthropicLLMService:
    def __init__(self):
        if (
            not settings.anthropic_api_key
            or settings.anthropic_api_key == "your_actual_anthropic_key_here"
        ):
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def _require_client(self):
        if self.client is None:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is missing. Please update ANTHROPIC_API_KEY in .env"
            )

    async def generate_text_response(
        self,
        *,
        model: str | None,
        system_prompt: str | None,
        user_message: str,
        conversation_history: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> str:
        self._require_client()

        messages = []

        for item in conversation_history or []:
            role = item.get("role", "user")
            content = item.get("content", "")

            # Claude Messages API accepts user/assistant messages.
            # System prompt is passed separately.
            if role in ["user", "assistant"] and content:
                messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        model_to_use = model or settings.anthropic_model_id

        def call_anthropic():
            response = self.client.messages.create(
                model=model_to_use,
                max_tokens=settings.anthropic_max_tokens,
                temperature=min(max(float(temperature or 0.7), 0.0), 1.0),
                system=system_prompt or "You are a helpful assistant.",
                messages=messages,
            )

            text_parts = []

            for block in response.content:
                if getattr(block, "type", None) == "text":
                    text_parts.append(block.text)

            return "\n".join(text_parts).strip()

        return await asyncio.to_thread(call_anthropic)


anthropic_llm_service = AnthropicLLMService()
