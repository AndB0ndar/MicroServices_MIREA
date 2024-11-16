import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from models import *
from schemas import *


async def get_location(db: AsyncSession, location_id: int):
    result = await db.execute(
        select(Location)
        .where(Location.id == location_id)
        .options(joinedload(Location.products))
    )
    return result.scalar_one_or_none()

async def get_locations(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Location)
        .offset(skip)
        .limit(limit)
        .options(joinedload(Location.products))
    )
    locations = result.unique().scalars().all()
    return locations

async def create_location(db: AsyncSession, location: LocationCreate):
    db_location = Location(name=location.name, address=location.address)
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)

    if location.products:
        result = await db.execute(
            select(Product)
            .filter(Product.id.in_(location.products))
        )
        products = result.scalars().all()
        db_location.products.extend(products)
        await db.commit()
        await db.refresh(db_location)

    return db_location


async def update_location(
        db: AsyncSession, location_id: int, location: LocationUpdate):
    result = await db.execute(
        select(Location)
        .options(joinedload(Location.products))
        .filter(Location.id == location_id)
    )
    db_location = result.scalars().unique().first()

    if not db_location:
        return None

    for key, value in location.dict(exclude_unset=True).items():
        if key == "products":
            continue
        setattr(db_location, key, value)

    if "products" in location.dict(exclude_unset=True):
        product_ids = location.products
        result = await db.execute(
            select(Product)
            .filter(Product.id.in_(product_ids))
        )
        products = result.scalars().all()
        db_location.products = products

    await db.commit()
    await db.refresh(db_location)

    return db_location

async def delete_location(db: AsyncSession, location_id: int):
    result = await db.execute(
        select(Location)
        .filter(Location.id == location_id)
    )
    db_location = result.scalars().unique().first()

    if not db_location:
        return None

    await db.delete(db_location)
    await db.commit()

    return db_location



async def get_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

async def get_products(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate):
    db_product = await get_product(db, product_id)
    if not db_product:
        return None
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: int):
    db_product = await get_product(db, product_id)
    if not db_product:
        return None

    await create_delivery_order(-1, db_product.id, db_product.name, 100)

    await db.delete(db_product)
    await db.commit()
    return db_product


async def make_purchase(db: AsyncSession, location_id: int, product_id: int, quantity: int):
    # Проверяем, существует ли локация
    result = await db.execute(
        select(Location).where(Location.id == location_id).options(joinedload(Location.products))
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Проверяем, связан ли продукт с этой локацией
    product = next((p for p in location.products if p.id == product_id), None)
    if not product:
        raise HTTPException(
            status_code=404, detail="Product not found in this location")

    # Проверяем наличие нужного количества продукта
    if product.stock < quantity:
        raise HTTPException(
            status_code=400, detail="Not enough stock for the product")

    # Вычитаем количество и сохраняем изменения
    product.stock -= quantity
    await db.commit()
    await db.refresh(product)

    return {
        "message": "Purchase successful",
        "location_id": location_id,
        "product_id": product_id,
        "remaining_stock": product.stock
    }


DELIVERY_SERVICE_URL = "http://orders_service:8000/orders"
async def create_delivery_order(
        location_id: int, product_id: int, product_name: str, quantity: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                DELIVERY_SERVICE_URL,
                json={
                    "location_id": location_id,
                    "product_id": product_id,
                    "product_name": product_name,
                    "quantity": quantity
                }
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Failed to create delivery order: {e}")

