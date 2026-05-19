import asyncio

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class AWSBedrockLLMService:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_default_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
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
        model_id = model or settings.aws_bedrock_model_id

        if not model_id or model_id == "your_enabled_bedrock_model_id_here":
            raise RuntimeError("AWS_BEDROCK_MODEL_ID is missing or not configured.")

        messages = []

        for item in conversation_history or []:
            role = item.get("role", "user")
            content = item.get("content", "")

            if role in ["user", "assistant"] and content:
                messages.append(
                    {
                        "role": role,
                        "content": [{"text": content}],
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": [{"text": user_message}],
            }
        )

        def call_bedrock():
            try:
                response = self.client.converse(
                    modelId=model_id,
                    messages=messages,
                    system=[
                        {
                            "text": system_prompt or "You are a helpful assistant."
                        }
                    ],
                    inferenceConfig={
                        "maxTokens": settings.aws_bedrock_max_tokens,
                        "temperature": float(temperature or 0.7),
                    },
                )

                content_blocks = response["output"]["message"].get("content", [])

                text_parts = [
                    block.get("text", "")
                    for block in content_blocks
                    if block.get("text")
                ]

                return "\n".join(text_parts).strip()

            except ClientError as exc:
                raise RuntimeError(f"AWS Bedrock failed: {exc}") from exc

        return await asyncio.to_thread(call_bedrock)


aws_bedrock_llm_service = AWSBedrockLLMService()
