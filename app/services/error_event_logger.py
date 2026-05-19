from app.services.mongo_event_logger import mongo_event_logger
from app.services.error_formatting import extract_error_message


async def log_error_event(
    *,
    company_id=None,
    session_id=None,
    channel: str = "unknown",
    route: str = "unknown",
    stage: str = "unknown",
    provider: str = "unknown",
    error: Exception | str,
    metadata: dict | None = None,
):
    error_text = extract_error_message(error)

    safe_metadata = metadata or {}
    safe_metadata.update(
        {
            "route": route,
            "stage": stage,
            "error_type": type(error).__name__ if not isinstance(error, str) else "Error",
        }
    )

    try:
        await mongo_event_logger.log_event(
            company_id=company_id or "unknown",
            session_id=session_id or "unknown",
            channel=channel,
            event_type="provider_error",
            provider=provider,
            text=error_text[:2000],
            metadata=safe_metadata,
        )
    except Exception as logging_error:
        # Never let error logging break the main API response.
        print(f"Failed to log provider_error event: {logging_error}")
