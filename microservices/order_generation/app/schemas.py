from pydantic import BaseModel


class Order(BaseModel):
    order_id: int
    customer_name: str
    address: str
    item: str
    quantity: int
