import asyncio
import json
import logging
import random
import uuid

import aio_pika

from .rabbitmq_pool import channel_pool
from .redis_pool import get_redis_pool

# Get a unique identifier for this consumer instance.
CONSUMER_ID = "payment_processing"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_payment(message: aio_pika.IncomingMessage, channel: aio_pika.Channel):
    async with get_redis_pool() as redis:
        # Construct a unique key for this consumer.
        unique_key = f"{CONSUMER_ID}-{message.message_id}"

        # Check for duplicate messages using Redis.
        if await redis.exists(unique_key):
            logger.warning(f"Duplicate message detected with ID: {unique_key}")
            return

        payment_data = json.loads(message.body.decode())

        try:
            logger.info(f"Processing payment for order {payment_data['order_id']}")

            # Simulate a delay for payment processing.
            await asyncio.sleep(1)

            # Randomly fail some payments for demonstration.
            if random.random() < 0.1:
                raise Exception("Random payment error!")

            # Payment successful, send event for successful payment.
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"order_id": payment_data["order_id"], "status": "success"}).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    message_id=str(uuid.uuid4()),
                ),
                routing_key="payment_success_queue",
            )

            logger.info(f"Payment for order {payment_data['order_id']} was successful")

            # On successful payment, push event to the shipping service.
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(
                        {
                            "order_id": payment_data["order_id"],
                            "customer_name": payment_data["customer_name"],
                            "address": payment_data["address"],
                            "item": payment_data["item"],
                            "quantity": payment_data["quantity"],
                        }
                    ).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    message_id=str(uuid.uuid4()),
                ),
                routing_key="shipping_queue",
            )

            # Store unique key in Redis with a TTL 1 hour to avoid processing the same message multiple times.
            await redis.setex(unique_key, 3600, "processed")

            # Acknowledge the message after processing payment.
            await message.ack()
        except Exception as e:
            logger.error(f"Error processing payment for order {payment_data['order_id']}: {e}")
            await message.reject(requeue=False)


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            queue = await channel.get_queue("payment_queue")
            async for message in queue:
                asyncio.create_task(process_payment(message, channel))


if __name__ == "__main__":
    asyncio.run(main())
