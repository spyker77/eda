import asyncio
import json
import logging

import aio_pika
from rabbitmq_pool import channel_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_shipping(message: aio_pika.IncomingMessage):
    order_data = json.loads(message.body.decode())

    try:
        logger.info(f"Packing order {order_data['order_id']} for {order_data['customer_name']}")

        # Simulate a delay for packing.
        await asyncio.sleep(2)

        logger.info(f"Order {order_data['order_id']} dispatched to {order_data['address']}")

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
