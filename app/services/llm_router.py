from openai import AsyncOpenAI

from app.core.config import settings
from app.services.huggingface_llm_service import huggingface_llm_service
from app.services.anthropic_llm_service import anthropic_llm_service
from app.services.gemini_llm_service import gemini_llm_service
from app.services.aws_bedrock_llm_service import aws_bedrock_llm_service
from app.services.ollama_llm_service import ollama_llm_service


class LLMRouter:
    def __init__(self):
        self.openai_client = None
        self.openrouter_client = None

        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            self.openai_client = AsyncOpenAI(
                api_key=settings.openai_api_key
            )

        if settings.openrouter_api_key and settings.openrouter_api_key != "your_openrouter_api_key_here":
            self.openrouter_client = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
            )

    def build_messages(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> list[dict]:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        if conversation_history:
            for item in conversation_history[-10:]:
                role = item.get("role", "user")
                content = item.get("content", "")

                if role in ["user", "assistant", "system"] and content:
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

        return messages

    async def generate_text_response(
        self,
        provider: str,
        model: str,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> str:
        provider = provider.lower().strip()

        messages = self.build_messages(
            system_prompt=system_prompt,
            user_message=user_message,
            conversation_history=conversation_history,
        )

        if provider == "openrouter":
            return await self._call_openrouter(
                model=model,
                messages=messages,
                temperature=temperature,
            )

        if provider == "openai":
            return await self._call_openai(
                model=model,
                messages=messages,
                temperature=temperature,
            )

        provider_normalized = (provider or "openrouter").lower().strip()

        provider_normalized = (provider or "openrouter").lower().strip()

        provider_normalized = (provider or "openrouter").lower().strip()

        provider_normalized = (provider or "openrouter").lower().strip()

        provider_normalized = (provider or "openrouter").lower().strip()

        if provider_normalized in ["ollama", "local_ollama", "ollama_local"]:
            return await ollama_llm_service.generate_text_response(
                model=model,
                system_prompt=system_prompt,
                user_message=user_message,
                conversation_history=conversation_history,
                temperature=temperature,
            )

        if provider_normalized in ["aws_bedrock", "bedrock", "amazon_bedrock"]:
            return await aws_bedrock_llm_service.generate_text_response(
                model=model,
                system_prompt=system_prompt,
                user_message=user_message,
                conversation_history=conversation_history,
                temperature=temperature,
            )

        if provider_normalized in ["gemini", "google", "google_gemini"]:
            return await gemini_llm_service.generate_text_response(
                model=model,
                system_prompt=system_prompt,
                user_message=user_message,
                conversation_history=conversation_history,
                temperature=temperature,
            )

        if provider_normalized in ["anthropic", "claude", "anthropic_claude"]:
            return await anthropic_llm_service.generate_text_response(
                model=model,
                system_prompt=system_prompt,
                user_message=user_message,
                conversation_history=conversation_history,
                temperature=temperature,
            )

        if provider_normalized in ["huggingface", "hf", "hugging_face"]:
            return await huggingface_llm_service.generate_text_response(
                model=model,
                system_prompt=system_prompt,
                user_message=user_message,
                conversation_history=conversation_history,
                temperature=temperature,
            )

        raise ValueError(f"Unsupported LLM provider: {provider}")

    async def _call_openrouter(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
    ) -> str:
        if self.openrouter_client is None:
            raise ValueError(
                "OpenRouter API key is missing. Please update OPENROUTER_API_KEY in .env"
            )

        response = await self.openrouter_client.chat.completions.create(
            model=model or settings.openrouter_model,
            messages=messages,
            temperature=temperature,
        )

        content = response.choices[0].message.content

        if not content:
            return "I received your message, but I could not generate a proper response."

        return content

    async def _call_openai(
        self,
        model: str,
        messages: list[dict],
        temperature: float,
    ) -> str:
        if self.openai_client is None:
            raise ValueError(
                "OpenAI API key is missing. Please update OPENAI_API_KEY in .env"
            )

        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        content = response.choices[0].message.content

        if not content:
            return "I received your message, but I could not generate a proper response."

        return content


llm_router = LLMRouter()
