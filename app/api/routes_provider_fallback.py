from fastapi import APIRouter, Header, HTTPException, Query

from app.core.config import settings
from app.services.llm_fallback_router import llm_fallback_router

router = APIRouter()


def require_admin_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_API_KEY is not configured on the server",
        )

    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin API key",
        )

    return True


@router.get("/fallback-test")
async def fallback_test(
    message: str = Query(default="Say hello in one short sentence."),
    primary_provider: str = Query(default="bad_provider"),
    primary_model: str | None = Query(default=None),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    try:
        result = await llm_fallback_router.generate_text_response_with_fallback(
            primary_provider=primary_provider,
            primary_model=primary_model,
            system_prompt="You are a helpful assistant. Keep answers short and clear.",
            user_message=message,
            conversation_history=[],
            temperature=0.5,
        )

        return {
            "status": "ok",
            "message": message,
            "provider_used": result["provider_used"],
            "model_used": result["model_used"],
            "fallback_used": result["fallback_used"],
            "response": result["text"],
            "attempts": result["attempts"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Fallback test failed: {str(exc)}",
        )
