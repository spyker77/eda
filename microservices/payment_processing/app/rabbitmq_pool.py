import os

import aio_pika
from aio_pika.pool import Pool

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


async def get_connection() -> aio_pika.RobustConnection:
    return await aio_pika.connect_robust(RABBITMQ_URL)


async def get_channel() -> aio_pika.Channel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


connection_pool = Pool(get_connection, max_size=2)
channel_pool = Pool(get_channel, max_size=10)
