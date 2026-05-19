from datetime import datetime, timezone
from typing import Any

from app.core.config import settings
from app.db.mongo import get_mongo_database, is_mongodb_enabled


def safe_str(value):
    return str(value) if value is not None else None


class MongoEventLogger:
    async def log_event(
        self,
        *,
        company_id: Any = None,
        session_id: Any = None,
        channel: str,
        event_type: str,
        provider: str | None = None,
        text: str | None = None,
        metadata: dict | None = None,
    ):
        if not is_mongodb_enabled():
            return None

        try:
            db = get_mongo_database()
            collection_name = settings.mongodb_events_collection or "events"

            event_doc = {
                "company_id": safe_str(company_id),
                "session_id": safe_str(session_id),
                "channel": channel,
                "event_type": event_type,
                "provider": provider,
                "text": text,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
            }

            result = await db[collection_name].insert_one(event_doc)
            return str(result.inserted_id)

        except Exception as exc:
            print(f"Mongo event logging failed: {exc}")
            return None


mongo_event_logger = MongoEventLogger()
