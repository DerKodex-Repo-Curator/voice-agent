from fastapi import APIRouter, Header, HTTPException, Query

from app.core.config import settings
from app.db.mongo import get_mongo_database

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


@router.get("/errors/recent")
async def recent_provider_errors(
    limit: int = Query(default=10, ge=1, le=50),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    db = get_mongo_database()

    if db is None:
        raise HTTPException(
            status_code=500,
            detail="MongoDB is not configured or not available",
        )

    cursor = db["events"].find(
        {"event_type": "provider_error"}
    ).sort("created_at", -1).limit(limit)

    errors = []

    async for doc in cursor:
        errors.append(
            {
                "id": str(doc.get("_id")),
                "created_at": str(doc.get("created_at")),
                "company_id": doc.get("company_id"),
                "session_id": doc.get("session_id"),
                "channel": doc.get("channel"),
                "provider": doc.get("provider"),
                "error": doc.get("text"),
                "metadata": doc.get("metadata"),
            }
        )

    return {
        "status": "ok",
        "count": len(errors),
        "errors": errors,
    }
