from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import *
from schemas import *


async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
    order = Order(
        location_id=order_data.location_id,
        product_id=order_data.product_id,
        product_name=order_data.product_name,
        quantity=order_data.quantity,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

async def get_order(db: AsyncSession, order_id: int) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()

async def get_all_orders(db: AsyncSession):
    result = await db.execute(select(Order))
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        return None
    order.status = status
    await db.commit()
    await db.refresh(order)
    return order

async def delete_order(db: AsyncSession, order_id: int):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        return False
    await db.delete(order)
    await db.commit()
    return True

