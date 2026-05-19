from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.services.anthropic_llm_service import anthropic_llm_service

router = APIRouter()


@router.get("/test")
async def test_anthropic(
    message: str = Query(default="Say hello in one short sentence."),
):
    try:
        response = await anthropic_llm_service.generate_text_response(
            model=settings.anthropic_model_id,
            system_prompt="You are a concise helpful assistant.",
            user_message=message,
            conversation_history=[],
            temperature=0.5,
        )

        return {
            "provider": "anthropic",
            "model": settings.anthropic_model_id,
            "message": message,
            "response": response,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Anthropic test failed: {str(exc)}",
        )
