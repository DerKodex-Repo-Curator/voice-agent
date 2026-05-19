from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.services.ollama_llm_service import ollama_llm_service

router = APIRouter()


@router.get("/test")
async def test_ollama(
    message: str = Query(default="Say hello in one short sentence."),
):
    try:
        response = await ollama_llm_service.generate_text_response(
            model=settings.ollama_model_id,
            system_prompt="You are a concise helpful assistant.",
            user_message=message,
            conversation_history=[],
            temperature=0.5,
        )

        return {
            "provider": "ollama",
            "model": settings.ollama_model_id,
            "message": message,
            "response": response,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama test failed: {str(exc)}",
        )
