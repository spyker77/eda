import aio_pika
from quart import Blueprint, current_app
from quart_schema import tag, validate_response

from ..constants import ERROR_MESSAGES, Status
from .schemas import HealthResponse

NAME = "health"

health = Blueprint(NAME, __name__)


@health.get("/health")
@tag([NAME])
@validate_response(HealthResponse)
async def check_health() -> tuple[HealthResponse, int]:
    """Check service health"""
    channel_pool = current_app.channel_pool  # type: ignore

    try:
        async with channel_pool.acquire() as _:
            return HealthResponse(status=Status.OK.value, message="Service is operational"), 200

    except aio_pika.exceptions.AMQPError as e:
        current_app.logger.error(f"RabbitMQ error: {e}")
        return HealthResponse(status=Status.ERROR.value, message=ERROR_MESSAGES["RABBITMQ_ERROR"]), 503

    except Exception as e:
        current_app.logger.error(f"Unexpected error at /health/ endpoint: {e}")
        return HealthResponse(status=Status.ERROR.value, message=ERROR_MESSAGES["UNKNOWN_ERROR"]), 500
