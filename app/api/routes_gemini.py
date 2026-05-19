from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.services.gemini_llm_service import gemini_llm_service

router = APIRouter()


@router.get("/test")
async def test_gemini(
    message: str = Query(default="Say hello in one short sentence."),
):
    try:
        response = await gemini_llm_service.generate_text_response(
            model=settings.gemini_model_id,
            system_prompt="You are a concise helpful assistant.",
            user_message=message,
            conversation_history=[],
            temperature=0.5,
        )

        return {
            "provider": "gemini",
            "model": settings.gemini_model_id,
            "message": message,
            "response": response,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini test failed: {str(exc)}",
        )
