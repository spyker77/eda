import asyncio
import os

import aio_pika
from aio_pika.pool import Pool

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def get_connection() -> aio_pika.RobustConnection:
    return await aio_pika.connect_robust(RABBITMQ_URL)


async def get_channel() -> aio_pika.Channel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


loop = asyncio.get_event_loop()

connection_pool = Pool(get_connection, max_size=2, loop=loop)
channel_pool = Pool(get_channel, max_size=10, loop=loop)
