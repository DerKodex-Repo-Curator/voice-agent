from fastapi import APIRouter, HTTPException

from app.db.mongo import get_mongo_database, is_mongodb_enabled

router = APIRouter()


@router.get("/health")
async def mongo_health():
    if not is_mongodb_enabled():
        return {
            "mongodb": "disabled",
            "message": "Set USE_MONGODB=True, MONGODB_URL, and MONGODB_DATABASE to enable MongoDB.",
        }

    db = get_mongo_database()

    try:
        result = await db.command("ping")
        return {
            "mongodb": "connected",
            "result": result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"MongoDB connection failed: {str(exc)}",
        )
