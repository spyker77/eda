import asyncio
import json
import logging

import aio_pika

CONNECTION_STRING = "amqp://guest:guest@rabbitmq/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_shipping(message: aio_pika.IncomingMessage):
    order_data = json.loads(message.body.decode())

    try:
        logger.info(
            f"Packing order {order_data['order_id']} for {order_data['customer_name']}"
        )

        await asyncio.sleep(2)  # Simulate a delay for packing

        logger.info(
            f"Order {order_data['order_id']} dispatched to {order_data['address']}"
        )

        # Acknowledge the message after shipping
        await message.ack()
    except Exception as e:
        logger.error(f"Error shipping order {order_data['order_id']}: {e}")


async def main():
    connection = await aio_pika.connect_robust(CONNECTION_STRING)
    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue("shipping_queue", durable=True)

        async for message in queue:
            await handle_shipping(message)


if __name__ == "__main__":
    asyncio.run(main())
