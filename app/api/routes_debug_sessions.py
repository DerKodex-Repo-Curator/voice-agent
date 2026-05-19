from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.db.models import ConversationMessage, ConversationSession
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


def safe_str(value):
    return str(value) if value is not None else None


def serialize_session(session):
    return {
        "session_id": safe_str(getattr(session, "id", None)),
        "company_id": safe_str(getattr(session, "company_id", None)),
        "persona_id": safe_str(getattr(session, "persona_id", None)),
        "channel": getattr(session, "channel", None),
        "status": getattr(session, "status", None),
        "metadata": getattr(session, "metadata_json", None),
        "created_at": safe_str(getattr(session, "created_at", None)),
        "updated_at": safe_str(getattr(session, "updated_at", None)),
    }


def serialize_message(message):
    return {
        "message_id": safe_str(getattr(message, "id", None)),
        "session_id": safe_str(getattr(message, "session_id", None)),
        "role": getattr(message, "role", None),
        "content": getattr(message, "content", None),
        "message_type": getattr(message, "message_type", None),
        "metadata": getattr(message, "metadata_json", None),
        "created_at": safe_str(getattr(message, "created_at", None)),
    }


def serialize_mongo_event(doc):
    return {
        "id": safe_str(doc.get("_id")),
        "created_at": safe_str(doc.get("created_at")),
        "company_id": doc.get("company_id"),
        "session_id": doc.get("session_id"),
        "channel": doc.get("channel"),
        "event_type": doc.get("event_type"),
        "provider": doc.get("provider"),
        "text": doc.get("text"),
        "metadata": doc.get("metadata"),
    }


@router.get("/sessions/recent")
async def recent_sessions(
    limit: int = Query(default=10, ge=1, le=50),
    _: bool = Depends(require_admin_key),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConversationSession)
        .order_by(ConversationSession.created_at.desc())
        .limit(limit)
    )

    sessions = result.scalars().all()

    return {
        "status": "ok",
        "count": len(sessions),
        "sessions": [serialize_session(session) for session in sessions],
    }


@router.get("/sessions/{session_id}")
async def session_debug_detail(
    session_id: UUID,
    mongo_event_limit: int = Query(default=50, ge=1, le=200),
    _: bool = Depends(require_admin_key),
    db: AsyncSession = Depends(get_db),
):
    session_result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == session_id
        )
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.created_at.asc())
    )
    messages = messages_result.scalars().all()

    mongo_events = []
    mongo_errors = []

    mongo_db = get_mongo_database()

    if mongo_db is not None:
        cursor = mongo_db["events"].find(
            {"session_id": str(session_id)}
        ).sort("created_at", -1).limit(mongo_event_limit)

        async for doc in cursor:
            event = serialize_mongo_event(doc)
            mongo_events.append(event)

            if event.get("event_type") == "provider_error":
                mongo_errors.append(event)

    return {
        "status": "ok",
        "session": serialize_session(session),
        "postgres_messages": [serialize_message(message) for message in messages],
        "mongo_events_count": len(mongo_events),
        "mongo_events": mongo_events,
        "provider_errors_count": len(mongo_errors),
        "provider_errors": mongo_errors,
    }
