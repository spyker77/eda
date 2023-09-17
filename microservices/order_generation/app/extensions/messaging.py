import uuid

import aio_pika

from .rabbitmq import ChannelPool


async def publish_message(channel_pool: ChannelPool, data: bytes, routing_key: str) -> None:
    """Publish a message to RabbitMQ using a given channel pool."""
    async with channel_pool.acquire() as channel:
        message = aio_pika.Message(
            body=data,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            message_id=str(uuid.uuid4()),
        )
        await channel.default_exchange.publish(message, routing_key=routing_key)
