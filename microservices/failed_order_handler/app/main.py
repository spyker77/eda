import asyncio
import json
import logging

import aio_pika

CONNECTION_STRING = "amqp://guest:guest@rabbitmq/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_dead_letter(message: aio_pika.IncomingMessage):
    order_data = json.loads(message.body.decode())
    logger.error(
        f"Failed order: {order_data['order_id']}. Reason: {message.headers.get('x-death')[0].get('reason')}"
    )

    # TODO: Add notification logic. For instance, you can notify a support team about this failed order.

    await message.ack()


async def main():
    connection = await aio_pika.connect_robust(CONNECTION_STRING)
    async with connection:
        channel = await connection.channel()

        dead_letter_queue = await channel.declare_queue(
            "dead_letter_queue", durable=True
        )

        async for message in dead_letter_queue:
            await handle_dead_letter(message)


if __name__ == "__main__":
    asyncio.run(main())
