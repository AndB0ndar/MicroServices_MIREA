from pydantic import BaseModel
from typing import Optional

class OrderCreate(BaseModel):
    """
    Schema for creating a new order.
    Fields:
        - location_id: ID of the location where the order is placed.
        - product_id: ID of the product being ordered.
        - product_name: Name of the product being ordered.
        - quantity: Quantity of the product to be ordered.
    """
    location_id: int
    product_id: int
    product_name: str
    quantity: int

class OrderUpdate(BaseModel):
    """
    Schema for updating the status of an existing order.
    Fields:
        - status: New status for the order
            (e.g., 'pending', 'completed', 'canceled').
    """
    status: str

class OrderResponse(BaseModel):
    """
    Schema for returning order details to the client.
    Fields:
        - id: Unique identifier of the order.
        - location_id: ID of the location where the order is placed.
        - product_id: ID of the product being ordered.
        - product_name: Name of the product being ordered.
        - quantity: Quantity of the product ordered.
        - status: Current status of the order.
    """
    id: int
    location_id: int
    product_id: int
    product_name: str
    quantity: int
    status: str

    class Config:
        orm_mode = True

