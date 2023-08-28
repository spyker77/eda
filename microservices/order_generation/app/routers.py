import json
import logging

import aio_pika
from fastapi import APIRouter, HTTPException
from rabbitmq_pool import channel_pool
from schemas import Order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create_order/")
async def place_order(order: Order) -> dict[str, str]:
    order_data = order.dict()
    try:
        async with channel_pool.acquire() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(order_data).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="orders_queue",
            )
            return {"status": "success", "message": "Order placed successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to place order")


@router.get("/health")
async def health_check() -> dict[str, str]:
    try:
        # Simply trying to get a channel will ensure connection health.
        async with channel_pool.acquire() as _:
            return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Cannot connect to RabbitMQ")
