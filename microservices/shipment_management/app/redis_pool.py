import os
from contextlib import asynccontextmanager

from redis import asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL")


@asynccontextmanager
async def get_redis_pool():
    connection = aioredis.Redis.from_url(REDIS_URL)
    try:
        yield connection
    finally:
        await connection.close()
