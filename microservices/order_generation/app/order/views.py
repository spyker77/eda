import aio_pika
from quart import Blueprint, current_app
from quart_schema import tag, validate_request, validate_response

from ..constants import ERROR_MESSAGES, Status
from ..extensions.messaging import publish_message
from ..utils import serialize_model
from .schemas import CreateOrderResponse, Order

NAME = "order"

order = Blueprint(NAME, __name__)


@order.post("/order")
@tag([NAME])
@validate_request(Order)
@validate_response(CreateOrderResponse, 201)
async def create_order(data: Order) -> tuple[CreateOrderResponse, int]:
    """Create order"""
    channel_pool = current_app.channel_pool  # type: ignore

    try:
        await publish_message(channel_pool, serialize_model(data), "orders_queue")
        return CreateOrderResponse(status=Status.SUCCESS.value, message="Order created successfully"), 201

    except aio_pika.exceptions.AMQPError as e:
        current_app.logger.error(f"RabbitMQ error with data {data}: {e}")
        return CreateOrderResponse(status=Status.ERROR.value, message=ERROR_MESSAGES["RABBITMQ_ERROR"]), 503

    except Exception as e:
        current_app.logger.error(f"Unexpected error with data {data}: {e}")
        return CreateOrderResponse(status=Status.ERROR.value, message=ERROR_MESSAGES["UNKNOWN_ERROR"]), 500
