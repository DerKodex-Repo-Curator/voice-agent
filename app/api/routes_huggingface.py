from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.services.huggingface_llm_service import huggingface_llm_service

router = APIRouter()


@router.get("/test")
async def test_huggingface(
    message: str = Query(default="Say hello in one short sentence."),
):
    try:
        response = await huggingface_llm_service.generate_text_response(
            model=settings.huggingface_model_id,
            system_prompt="You are a concise helpful assistant.",
            user_message=message,
            conversation_history=[],
            temperature=0.5,
        )

        return {
            "provider": "huggingface",
            "model": settings.huggingface_model_id,
            "message": message,
            "response": response,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Hugging Face test failed: {str(exc)}",
        )
