from time import perf_counter

from fastapi import APIRouter, Header, HTTPException, Query

from app.core.config import settings
from app.services.voice_provider_router import voice_provider_router
from app.services.mongo_event_logger import mongo_event_logger

router = APIRouter()


def require_admin_key(
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    if not settings.admin_api_key:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY is not configured")

    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")

    return True


@router.post("/tts")
async def benchmark_tts_providers(
    text: str = Query(default="Hello, this is a provider benchmark test in English."),
    providers: str = Query(default="azure_speech,cartesia"),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    provider_list = [
        provider.strip()
        for provider in providers.split(",")
        if provider.strip()
    ]

    if not provider_list:
        raise HTTPException(status_code=400, detail="At least one provider is required")

    results = []

    for provider in provider_list:
        started_at = perf_counter()

        try:
            audio_url = await voice_provider_router.synthesize_speech(
                tts_provider=provider,
                text=text,
            )

            latency_ms = round((perf_counter() - started_at) * 1000, 2)

            result = {
                "provider": provider,
                "status": "success",
                "latency_ms": latency_ms,
                "audio_url": audio_url,
            }

        except Exception as exc:
            latency_ms = round((perf_counter() - started_at) * 1000, 2)

            result = {
                "provider": provider,
                "status": "failed",
                "latency_ms": latency_ms,
                "error": str(exc),
            }

        results.append(result)

    fastest = None
    successful = [row for row in results if row["status"] == "success"]

    if successful:
        fastest = min(successful, key=lambda row: row["latency_ms"])

    try:
        await mongo_event_logger.log_event(
            company_id="benchmark",
            session_id="benchmark",
            channel="benchmark",
            event_type="tts_provider_benchmark",
            provider=",".join(provider_list),
            text=text,
            metadata={
                "results": results,
                "fastest": fastest,
            },
        )
    except Exception as exc:
        print(f"Benchmark Mongo logging failed: {exc}")

    return {
        "status": "ok",
        "benchmark_type": "tts",
        "text": text,
        "providers": provider_list,
        "fastest": fastest,
        "results": results,
    }


@router.get("/recent")
async def recent_benchmarks(
    limit: int = Query(default=10, ge=1, le=50),
    x_admin_api_key: str | None = Header(default=None, alias="X-Admin-API-Key"),
):
    require_admin_key(x_admin_api_key)

    from app.db.mongo import get_mongo_database

    db = get_mongo_database()

    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB is not configured")

    cursor = db["events"].find(
        {"event_type": "tts_provider_benchmark"}
    ).sort("created_at", -1).limit(limit)

    benchmarks = []

    async for doc in cursor:
        benchmarks.append(
            {
                "created_at": str(doc.get("created_at")),
                "provider": doc.get("provider"),
                "text": doc.get("text"),
                "metadata": doc.get("metadata"),
            }
        )

    return {
        "status": "ok",
        "count": len(benchmarks),
        "benchmarks": benchmarks,
    }
