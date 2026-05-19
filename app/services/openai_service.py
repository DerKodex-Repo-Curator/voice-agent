from openai import AsyncOpenAI

from app.core.config import settings


class OpenAIService:
    def __init__(self):
        self.openai_client = None
        self.openrouter_client = None

        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

        if settings.openrouter_api_key and settings.openrouter_api_key != "your_openrouter_api_key_here":
            self.openrouter_client = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
            )

    async def generate_text_response(
        self,
        provider: str,
        model: str,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> str:
        history_messages = []

        if conversation_history:
            for item in conversation_history[-10:]:
                history_messages.append(
                    {
                        "role": item.get("role", "user"),
                        "content": item.get("content", ""),
                    }
                )

        messages = [
            {"role": "system", "content": system_prompt},
            *history_messages,
            {"role": "user", "content": user_message},
        ]

        if provider == "openrouter":
            if self.openrouter_client is None:
                raise ValueError(
                    "OpenRouter API key is missing. Please update OPENROUTER_API_KEY in .env"
                )

            response = await self.openrouter_client.chat.completions.create(
                model=model or settings.openrouter_model,
                messages=messages,
                temperature=temperature,
            )

            return response.choices[0].message.content

        if provider == "openai":
            if self.openai_client is None:
                raise ValueError(
                    "OpenAI API key is missing. Please update OPENAI_API_KEY in .env"
                )

            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )

            return response.choices[0].message.content

        raise ValueError(f"Unsupported LLM provider: {provider}")


openai_service = OpenAIService()
