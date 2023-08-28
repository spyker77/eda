import asyncio
import json
import logging
import random

import aio_pika
from rabbitmq_pool import channel_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_payment(message: aio_pika.IncomingMessage, channel):
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
                body=json.dumps(
                    {"order_id": payment_data["order_id"], "status": "success"}
                ).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
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
            ),
            routing_key="shipping_queue",
        )

        # Acknowledge the message after processing payment.
        await message.ack()
    except Exception as e:
        # Payment failed, send event for failed payment.
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(
                    {
                        "order_id": payment_data["order_id"],
                        "status": "failed",
                        "reason": str(e),
                    }
                ).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key="payment_failed_queue",
        )

        logger.error(
            f"Error processing payment for order {payment_data['order_id']}: {e}"
        )


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            queue = await channel.declare_queue("payment_queue", durable=True)

            async for message in queue:
                asyncio.create_task(process_payment(message, channel))


if __name__ == "__main__":
    asyncio.run(main())
