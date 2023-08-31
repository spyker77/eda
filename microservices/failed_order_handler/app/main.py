import asyncio
import json
import logging

import aio_pika
from rabbitmq_pool import channel_pool
from redis_pool import get_redis_pool

# Get a unique identifier for this consumer instance.
CONSUMER_ID = "failed_order_handler"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_dead_letter(message: aio_pika.IncomingMessage):
    async with get_redis_pool() as redis:
        # Construct a unique key for this consumer.
        unique_key = f"{CONSUMER_ID}-{message.message_id}"

        # Check for duplicate messages using Redis.
        if await redis.exists(unique_key):
            logger.warning(f"Duplicate message detected with ID: {unique_key}")
            return

        order_data = json.loads(message.body.decode())

        logger.error(
            f"Failed order: {order_data['order_id']}. Reason: {message.headers.get('x-death')[0].get('reason')}"
        )

        # TODO: Add notification logic. For instance, you can notify a support team about this failed order.

        # Store unique key in Redis with a TTL 1 hour to avoid processing the same message multiple times.
        await redis.setex(unique_key, 3600, "processed")

        # Acknowledge the message after handling it.
        await message.ack()


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            dead_letter_queue = await channel.get_queue("dead_letter_queue")
            async for message in dead_letter_queue:
                asyncio.create_task(handle_dead_letter(message))


if __name__ == "__main__":
    asyncio.run(main())
