import json

import aio_pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

CONNECTION_STRING = "amqp://guest:guest@rabbitmq/"

app = FastAPI()

connection = None
channel = None


async def get_connection():
    global connection
    if connection is None:
        connection = await aio_pika.connect_robust(CONNECTION_STRING)
    return connection


async def get_channel():
    global channel
    if channel is None:
        channel = await (await get_connection()).channel()
    return channel


@app.on_event("startup")
async def startup_event():
    await get_connection()
    await get_channel()


@app.on_event("shutdown")
async def shutdown_event():
    global channel, connection
    if channel:
        await channel.close()
    if connection:
        await connection.close()


class Order(BaseModel):
    order_id: str
    customer_name: str
    item: str
    quantity: int


@app.post("/create_order/")
async def place_order(
    order_id: int,
    customer_name: str,
    address: str,
    item: str,
    quantity: int,
):
    order_data = {
        "order_id": order_id,
        "customer_name": customer_name,
        "address": address,
        "item": item,
        "quantity": quantity,
    }
    try:
        channel = await get_channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(order_data).encode()),
            routing_key="orders_queue",
        )
        return {"status": "Order placed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    try:
        # Simply trying to get a channel will ensure connection health
        await get_channel()
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Cannot connect to RabbitMQ")
