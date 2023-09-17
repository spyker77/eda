from pydantic import BaseModel


def serialize_model(model: BaseModel) -> bytes:
    """Serialize pydantic model to a JSON-encoded byte string."""
    return model.model_dump_json().encode()
