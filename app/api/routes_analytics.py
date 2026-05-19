from datetime import datetime, timedelta

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


@router.get("/provider-usage")
async def provider_usage(
    days: int = Query(default=7, ge=1, le=90),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    db = get_mongo_database()
    since = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {
            "$group": {
                "_id": {
                    "provider": "$provider",
                    "event_type": "$event_type",
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
    ]

    rows = []
    async for doc in await db["events"].aggregate(pipeline):
        rows.append(
            {
                "provider": doc["_id"].get("provider"),
                "event_type": doc["_id"].get("event_type"),
                "count": doc.get("count", 0),
            }
        )

    return {
        "status": "ok",
        "days": days,
        "provider_usage": rows,
    }


@router.get("/company-summary")
async def company_summary(
    company_id: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=90),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    db = get_mongo_database()
    since = datetime.utcnow() - timedelta(days=days)

    match_filter = {"created_at": {"$gte": since}}

    if company_id:
        match_filter["company_id"] = company_id

    total_events = await db["events"].count_documents(match_filter)

    error_filter = dict(match_filter)
    error_filter["event_type"] = "provider_error"
    total_errors = await db["events"].count_documents(error_filter)

    fallback_filter = dict(match_filter)
    fallback_filter["metadata.fallback_used"] = True
    total_fallbacks = await db["events"].count_documents(fallback_filter)

    voice_filter = dict(match_filter)
    voice_filter["event_type"] = {
        "$in": [
            "configured_voice_user_transcript",
            "configured_voice_assistant_message",
            "configured_voice_audio",
        ]
    }
    total_voice_events = await db["events"].count_documents(voice_filter)

    chat_filter = dict(match_filter)
    chat_filter["event_type"] = {
        "$in": [
            "chat_user_message",
            "chat_assistant_message",
        ]
    }
    total_chat_events = await db["events"].count_documents(chat_filter)

    latest_cursor = db["events"].find(match_filter).sort("created_at", -1).limit(10)

    latest_events = []
    async for doc in latest_cursor:
        latest_events.append(
            {
                "created_at": str(doc.get("created_at")),
                "company_id": doc.get("company_id"),
                "session_id": doc.get("session_id"),
                "event_type": doc.get("event_type"),
                "provider": doc.get("provider"),
                "metadata": doc.get("metadata"),
            }
        )

    return {
        "status": "ok",
        "company_id": company_id,
        "days": days,
        "summary": {
            "total_events": total_events,
            "total_errors": total_errors,
            "total_fallbacks": total_fallbacks,
            "total_voice_events": total_voice_events,
            "total_chat_events": total_chat_events,
        },
        "latest_events": latest_events,
    }
