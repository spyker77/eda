import asyncio
from typing import Optional

import aio_pika
from aio_pika.pool import Pool


class ChannelPool:
    """A pool manager for RabbitMQ channels.

    This class implements the Singleton pattern to ensure that only one instance
    of the channel pool is created. This instance can be accessed by instantiating
    the class with the RabbitMQ URL.
    """

    _instance: Optional["ChannelPool"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs) -> "ChannelPool":
        """Create a new instance or return the existing one."""
        if not cls._instance:
            cls._instance = super(ChannelPool, cls).__new__(cls)
        return cls._instance

    async def initialize(self, rabbitmq_url: Optional[str]) -> None:
        """Asynchronously initialize the pool with the provided RabbitMQ URL."""
        async with self._lock:
            if not hasattr(self, "_rabbitmq_url"):
                self._rabbitmq_url = rabbitmq_url
                self._connection_pool = Pool(self._get_connection, max_size=2)
                self._channel_pool = Pool(self._get_channel, max_size=10)

    async def _get_connection(self) -> aio_pika.abc.AbstractRobustConnection:
        """Get a robust connection to RabbitMQ."""
        return await aio_pika.connect_robust(self._rabbitmq_url)

    async def _get_channel(self) -> aio_pika.Channel:
        """Acquire a connection from the pool and get a channel."""
        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    def acquire(self) -> aio_pika.pool.PoolItemContextManager:
        """Acquire a channel from the pool."""
        return self._channel_pool.acquire()
