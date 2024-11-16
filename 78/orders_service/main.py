from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db
from schemas import *
from crud import *


async def startup_event():
    await init_db()

app = FastAPI(on_startup=[startup_event])


@app.post(
    "/orders",
    summary="Create a new order",
    description="Creates a new order with the provided details,"
        " such as location, product, quantity, and total price.",
    response_model=OrderResponse,
    responses={201: {"description": "Order successfully created"}}
)
async def create_order_endpoint(
        order: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await create_order(db, order)

@app.get(
    "/orders/{order_id}",
    summary="Get an order by ID",
    description="Fetches the details of a specific order using its unique ID.",
    response_model=OrderResponse,
    responses={
        200: {"description": "Order details retrieved successfully"},
        404: {"description": "Order not found"}
    }
)
async def get_order_endpoint(
        order_id: int, db: AsyncSession = Depends(get_db)):
    order = await get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get(
    "/orders",
    summary="Get all orders",
    description="Retrieves a list of all orders currently stored in the database.",
    response_model=list[OrderResponse],
    responses={200: {"description": "List of all orders retrieved successfully"}}
)
async def get_all_orders_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_all_orders(db)

@app.put(
    "/orders/{order_id}",
    summary="Update an order's status",
    description="Updates the status of a specific order using its ID."
        " Status can be 'pending', 'completed', or 'canceled'.",
    response_model=OrderResponse,
    responses={
        200: {"description": "Order status updated successfully"},
        404: {"description": "Order not found"}
    }
)
async def update_order_status_endpoint(
        order_id: int, order_update: OrderUpdate, 
        db: AsyncSession = Depends(get_db)):
    order = await update_order_status(db, order_id, order_update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.delete(
    "/orders/{order_id}",
    summary="Delete an order",
    description="Deletes a specific order"
        " from the database using its unique ID.",
    responses={
        200: {"description": "Order deleted successfully"},
        404: {"description": "Order not found"}
    }
)
async def delete_order_endpoint(
        order_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

