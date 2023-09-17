import asyncio
import json
import logging

import aio_pika

from .rabbitmq_pool import channel_pool
from .redis_pool import get_redis_pool

# Get a unique identifier for this consumer instance.
CONSUMER_ID = "notification"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_notification(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    async with get_redis_pool() as redis:
        # Construct a unique key for this consumer.
        unique_key = f"{CONSUMER_ID}-{message.message_id}"

        # Check for duplicate messages using Redis.
        if await redis.exists(unique_key):
            logger.warning(f"Duplicate message detected with ID: {unique_key}")
            return

        order_data = json.loads(message.body.decode())

        # For demonstration purposes, we'll simulate the process of sending a notification.
        # In a real-world scenario, you could integrate this with a notification service or
        # send an email, SMS, push notification, etc.
        try:
            logger.info(f"Sending notification for order {order_data['order_id']}")

            # Simulate a delay for sending the notification.
            await asyncio.sleep(0.5)

            # Notification was "sent" successfully.
            logger.info(f"Notification for order {order_data['order_id']} was sent successfully")

            # Store unique key in Redis with a TTL 1 hour to avoid processing the same message multiple times.
            await redis.setex(unique_key, 3600, "processed")

            # Acknowledge the message after sending the notification.
            await message.ack()
        except Exception as e:
            logger.error(f"Error sending notification for order {order_data['order_id']}: {e}")


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            queue = await channel.get_queue("notification_queue")
            async for message in queue:
                asyncio.create_task(send_notification(message, channel))


if __name__ == "__main__":
    asyncio.run(main())
