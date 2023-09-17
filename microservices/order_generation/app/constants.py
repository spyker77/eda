from enum import Enum


class Status(Enum):
    OK = "ok"
    SUCCESS = "success"
    ERROR = "error"


ERROR_MESSAGES = {
    "RABBITMQ_ERROR": "Failed to place order due to a RabbitMQ error",
    "UNKNOWN_ERROR": "Failed to place order due to an unknown error",
}
