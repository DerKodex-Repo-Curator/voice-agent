import inspect

import certifi

try:
    from pymongo import AsyncMongoClient
except ImportError:
    from pymongo.asynchronous import AsyncMongoClient

from app.core.config import settings


mongo_client = None


def is_mongodb_enabled() -> bool:
    return bool(
        settings.use_mongodb
        and settings.mongodb_url
        and settings.mongodb_database
    )


def get_mongo_client():
    global mongo_client

    if not is_mongodb_enabled():
        return None

    if mongo_client is None:
        mongo_client = AsyncMongoClient(
            settings.mongodb_url,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
        )

    return mongo_client


def get_mongo_database():
    client = get_mongo_client()

    if client is None:
        return None

    return client[settings.mongodb_database]


async def close_mongo_client():
    global mongo_client

    if mongo_client is not None:
        result = mongo_client.close()

        if inspect.isawaitable(result):
            await result

        mongo_client = None
