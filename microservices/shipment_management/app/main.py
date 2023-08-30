import asyncio
import json
import logging

import aio_pika
from rabbitmq_pool import channel_pool
from redis_pool import get_redis_pool

# Get a unique identifier for this consumer instance.
CONSUMER_ID = "shipment_management"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_shipping(message: aio_pika.IncomingMessage):
    async with get_redis_pool() as redis:
        # Construct a unique key for this consumer.
        unique_key = f"{CONSUMER_ID}-{message.message_id}"

        # Check for duplicate messages using Redis.
        if await redis.exists(unique_key):
            logger.warning(f"Duplicate message detected with ID: {unique_key}")
            return

        order_data = json.loads(message.body.decode())

        try:
            logger.info(f"Packing order {order_data['order_id']} for {order_data['customer_name']}")

            # Simulate a delay for packing.
            await asyncio.sleep(2)

            logger.info(f"Order {order_data['order_id']} dispatched to {order_data['address']}")

            # Store unique key in Redis with a TTL 1 hour to avoid processing the same message multiple times.
            await redis.setex(unique_key, 3600, "processed")

            # Acknowledge the message after shipping.
            await message.ack()
        except Exception as e:
            logger.error(f"Error shipping order {order_data['order_id']}: {e}")


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            queue = await channel.declare_queue("shipping_queue", durable=True)

            async for message in queue:
                asyncio.create_task(handle_shipping(message))


if __name__ == "__main__":
    asyncio.run(main())
