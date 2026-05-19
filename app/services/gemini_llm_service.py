import asyncio

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiLLMService:
    def __init__(self):
        api_key = settings.gemini_api_key or settings.google_api_key

        if not api_key or api_key == "your_actual_google_api_key_here":
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def _require_client(self):
        if self.client is None:
            raise RuntimeError(
                "GEMINI_API_KEY or GOOGLE_API_KEY is missing. Please update .env"
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

        model_to_use = model or settings.gemini_model_id

        prompt_parts = []

        for item in conversation_history or []:
            role = item.get("role", "user")
            content = item.get("content", "")
            if content:
                prompt_parts.append(f"{role.upper()}: {content}")

        prompt_parts.append(f"USER: {user_message}")

        prompt = "\n".join(prompt_parts)

        config = types.GenerateContentConfig(
            system_instruction=system_prompt or "You are a helpful assistant.",
            temperature=float(temperature or 0.7),
            max_output_tokens=settings.gemini_max_tokens,
        )

        def call_gemini():
            response = self.client.models.generate_content(
                model=model_to_use,
                contents=prompt,
                config=config,
            )
            return response.text or ""

        return await asyncio.to_thread(call_gemini)


gemini_llm_service = GeminiLLMService()
