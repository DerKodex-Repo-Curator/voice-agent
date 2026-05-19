import asyncio

from huggingface_hub import InferenceClient

from app.core.config import settings


class HuggingFaceLLMService:
    def __init__(self):
        token = settings.hf_token or settings.huggingface_api_key

        if not token or token == "your_huggingface_token_here":
            self.client = None
        else:
            self.client = InferenceClient(
                api_key=token,
                provider=settings.huggingface_provider or "auto",
            )

    def _require_client(self):
        if self.client is None:
            raise RuntimeError(
                "Hugging Face token is missing. Please set HF_TOKEN or HUGGINGFACE_API_KEY in .env"
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

        model_to_use = model or settings.huggingface_model_id

        def call_huggingface():
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=temperature,
                max_tokens=settings.huggingface_max_tokens,
            )

            return response.choices[0].message.content

        return await asyncio.to_thread(call_huggingface)


huggingface_llm_service = HuggingFaceLLMService()
