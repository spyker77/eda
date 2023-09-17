import asyncio
import json
import logging
import uuid

import aio_pika

from .rabbitmq_pool import channel_pool
from .redis_pool import get_redis_pool

# Get a unique identifier for this consumer instance.
CONSUMER_ID = "order_processing"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_order(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    async with get_redis_pool() as redis:
        # Construct a unique key for this consumer.
        unique_key = f"{CONSUMER_ID}-{message.message_id}"

        # Check for duplicate messages using Redis.
        if await redis.exists(unique_key):
            logger.warning(f"Duplicate message detected with ID: {unique_key}")
            return

        order_data = json.loads(message.body.decode())

        try:
            logger.info(
                f"Processing order {order_data['order_id']} for {order_data['quantity']} units of {order_data['item']}"
            )

            # Once order is successfully processed, broadcast it to the fanout exchange.
            processed_exchange = await channel.get_exchange("order_processed_exchange")
            await processed_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(
                        {
                            "order_id": order_data["order_id"],
                            "customer_name": order_data["customer_name"],
                            "address": order_data["address"],
                            "item": order_data["item"],
                            "quantity": order_data["quantity"],
                        }
                    ).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    message_id=str(uuid.uuid4()),
                ),
                routing_key="",
            )

            # Store unique key in Redis with a TTL 1 hour to avoid processing the same message multiple times.
            await redis.setex(unique_key, 3600, "processed")

            # Acknowledge the message after processing.
            await message.ack()
        except Exception as e:
            # If there's any exception in order processing, we don't acknowledge the message,
            # so it can be sent to the dead letter queue.
            logger.error(f"Error processing order {order_data['order_id']}: {e}")
            await message.reject(requeue=False)


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            queue = await channel.get_queue("orders_queue")
            async for message in queue:
                logger.info(f"Received message: {message.body.decode()}")
                asyncio.create_task(process_order(message, channel))


if __name__ == "__main__":
    asyncio.run(main())
