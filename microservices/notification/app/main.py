import asyncio
import json
import logging

import aio_pika
from rabbitmq_pool import channel_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_notification(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
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

        # Acknowledge the message after sending the notification.
        await message.ack()
    except Exception as e:
        logger.error(f"Error sending notification for order {order_data['order_id']}: {e}")


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            processed_exchange = await channel.declare_exchange(
                "order_processed_exchange", aio_pika.ExchangeType.FANOUT
            )
            queue = await channel.declare_queue("notification_queue", durable=True)
            await queue.bind(processed_exchange)

            async for message in queue:
                asyncio.create_task(send_notification(message, channel))


if __name__ == "__main__":
    asyncio.run(main())
