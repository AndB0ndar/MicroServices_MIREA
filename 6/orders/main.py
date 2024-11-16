import json
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, HTTPException


app = FastAPI()

@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    with open("openapi.json", 'w') as fin:
        json.dump(openapi_data, fin)


class OrderStatus(str, Enum):
    """
    Enum representing the various statuses an order can have.
    This helps standardize the order states throughout the application.

    Attributes:
    - pending: The order is awaiting processing.
    - in_progress: The order is currently being processed.
    - completed: The order has been successfully completed.
    - canceled: The order has been canceled and will not be processed.
    """
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"


class Order(BaseModel):
    """
    Represents an order in the system.

    Attributes:
    - order_id: Unique identifier for the order (int).
    - product_id: Identifier for the product being ordered (int).
    - quantity: Quantity of the product to order (int).
    - source_warehouse_id: (Optional) ID of the warehouse from which the product is sourced (int).
    - destination_warehouse_id: (Optional) ID of the warehouse to which the product is sent (int).
    - supplier_id: (Optional) ID of the supplier of the product (int).
    - status: Current status of the order, defaults to 'pending' (OrderStatus).
    """
    order_id: int
    product_id: int
    quantity: int
    source_warehouse_id: Optional[int] = None
    destination_warehouse_id: Optional[int] = None
    supplier_id: Optional[int] = None
    status: OrderStatus = OrderStatus.pending


orders_db: List[Order] = []


@app.post("/orders/", response_model=Order)
async def create_order(order: Order):
    """
    Creates a new order and stores it in the orders database.

    Parameters:
    - **order**: An Order object containing the details of the order to be created.

    Returns:
    - The created Order object.
    """
    orders_db.append(order)
    return order


@app.get("/orders/", response_model=List[Order])
async def get_orders():
    """
    Retrieves a list of all orders in the system.

    Returns:
    - A list of Order objects representing all existing orders.
    """
    return orders_db


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """
    Retrieves a specific order by its unique ID.

    Parameters:
    - **order_id**: The unique identifier of the order to retrieve.

    Returns:
    - The Order object corresponding to the specified ID.

    Raises:
    - HTTPException: If the order is not found (404).
    """
    for order in orders_db:
        if order.order_id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, status: OrderStatus):
    """
    Updates the status of an existing order.

    Parameters:
    - **order_id**: The unique identifier of the order to update.
    - **status**: The new status to set for the order.

    Returns:
    - The updated Order object.

    Raises:
    - HTTPException: If the order is not found (404).
    """
    for order in orders_db:
        if order.order_id == order_id:
            order.status = status
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.delete("/orders/{order_id}", response_model=dict)
async def delete_order(order_id: int):
    """
    Deletes an existing order by its unique ID.

    Parameters:
    - **order_id**: The unique identifier of the order to delete.

    Returns:
    - A message indicating the deletion of the order.

    Raises:
    - HTTPException: If the order is not found (404).
    """
    for i, order in enumerate(orders_db):
        if order.order_id == order_id:
            del orders_db[i]
            return {"message": "Order deleted"}
    raise HTTPException(status_code=404, detail="Order not found")

