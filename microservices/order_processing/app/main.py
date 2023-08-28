import asyncio
import json
import logging

import aio_pika
from rabbitmq_pool import channel_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_order(message: aio_pika.IncomingMessage, channel):
    order_data = json.loads(message.body.decode())

    try:
        logger.info(
            f"Processing order {order_data['order_id']} for {order_data['quantity']} units of {order_data['item']}"
        )

        # Once order is successfully processed, forward it to the payment service.
        await channel.default_exchange.publish(
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
            ),
            routing_key="payment_queue",
        )

        # Acknowledge the message after processing.
        await message.ack()
    except Exception as e:
        # If there's any exception in order processing, we don't acknowledge the message,
        # so it can be sent to the dead letter queue.
        logger.error(f"Error processing order {order_data['order_id']}: {e}")


async def main():
    async with channel_pool:
        async with channel_pool.acquire() as channel:
            dead_letter_exchange = await channel.declare_exchange(
                "dead_letter", "direct"
            )
            dead_letter_queue = await channel.declare_queue(
                "dead_letter_queue", durable=True
            )
            await dead_letter_queue.bind(dead_letter_exchange, "rejected")

            arguments = {
                "x-dead-letter-exchange": "dead_letter",
                "x-dead-letter-routing-key": "rejected",
            }

            queue = await channel.declare_queue(
                "orders_queue", durable=True, arguments=arguments
            )

            async for message in queue:
                logger.info(f"Received message: {message.body.decode()}")
                asyncio.create_task(process_order(message, channel))


if __name__ == "__main__":
    asyncio.run(main())
