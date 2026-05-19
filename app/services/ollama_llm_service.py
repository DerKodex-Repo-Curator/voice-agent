import asyncio

import httpx

from app.core.config import settings


class OllamaLLMService:
    async def generate_text_response(
        self,
        *,
        model: str | None,
        system_prompt: str | None,
        user_message: str,
        conversation_history: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> str:
        model_to_use = model or settings.ollama_model_id

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        for item in conversation_history or []:
            role = item.get("role", "user")
            content = item.get("content", "")

            if role in ["user", "assistant", "system"] and content:
                messages.append({
                    "role": role,
                    "content": content,
                })

        messages.append({
            "role": "user",
            "content": user_message,
        })

        payload = {
            "model": model_to_use,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(temperature or 0.7),
                "num_predict": settings.ollama_max_tokens,
            },
        }

        async def call_ollama():
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                    json=payload,
                )

            if response.status_code >= 400:
                raise RuntimeError(
                    f"Ollama failed: {response.status_code} {response.text}"
                )

            data = response.json()
            return data.get("message", {}).get("content", "").strip()

        return await call_ollama()


ollama_llm_service = OllamaLLMService()
