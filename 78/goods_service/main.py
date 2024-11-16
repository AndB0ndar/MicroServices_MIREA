from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db
from schemas import *
from crud import *


async def startup_event():
    await init_db()

app = FastAPI(on_startup=[startup_event])


@app.get("/locations", response_model=list[LocationOut])
@app.get(
    "/locations",
    summary="Retrieve a list of locations",
    description="Fetches a paginated list of all locations."
        " You can specify `skip` to offset the results"
        " and `limit` to control the number of items returned.",
    response_model=list[LocationOut],
    responses={
        200: {"description": "List of locations retrieved successfully"}
    }
)
async def read_locations(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_locations(db, skip=skip, limit=limit)

@app.get(
    "/locations/{location_id}",
    summary="Retrieve a specific location by ID",
    description="Fetches details of a specific location using its unique ID.",
    response_model=LocationOut,
    responses={
        200: {"description": "Location details retrieved successfully"},
        404: {"description": "Location not found"}
    }
)
async def read_location(location_id: int, db: AsyncSession = Depends(get_db)):
    location = await get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@app.post(
    "/locations",
    summary="Create a new location",
    description="Creates a new location with the specified details.",
    response_model=LocationOut,
    responses={
        201: {"description": "Location created successfully"}
    }
)
async def create_new_location(location: LocationCreate, db: AsyncSession = Depends(get_db)):
    return await create_location(db, location)

@app.put(
    "/locations/{location_id}",
    summary="Update an existing location",
    description="Updates the details of"
        " a specific location using its unique ID."
        " Returns the updated location details.",
    response_model=int,
    responses={
        200: {"description": "Location updated successfully"},
        404: {"description": "Location not found"}
    }
)
async def update_existing_location(location_id: int, location: LocationUpdate, db: AsyncSession = Depends(get_db)):
    updated_location = await update_location(db, location_id, location)
    if not updated_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return 1

@app.delete(
    "/locations/{location_id}",
    summary="Delete a specific location",
    description="Deletes a specific location using its unique ID."
        " Returns the details of the deleted location.",
    response_model=LocationOut,
    responses={
        200: {"description": "Location deleted successfully"},
        404: {"description": "Location not found"}
    }
)
async def delete_existing_location(location_id: int, db: AsyncSession = Depends(get_db)):
    deleted_location = await delete_location(db, location_id)
    if not deleted_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return deleted_location



@app.get(
    "/products",
    summary="Retrieve a list of products",
    description="Fetches a paginated list of all products."
        " You can specify `skip` to offset the results"
        " and `limit` to control the number of items returned.",
    response_model=list[ProductOut],
    responses={
        200: {"description": "List of products retrieved successfully"}
    }
)
async def read_products(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_products(db, skip=skip, limit=limit)

@app.get(
    "/products/{product_id}",
    summary="Retrieve a specific product by ID",
    description="Fetches details of a specific product using its unique ID.",
    response_model=ProductOut,
    responses={
        200: {"description": "Product details retrieved successfully"},
        404: {"description": "Product not found"}
    }
)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post(
    "/products",
    summary="Create a new product",
    description="Creates a new product with the specified details,"
        " such as name, description, price, and stock quantity.",
    response_model=ProductOut,
    responses={
        201: {"description": "Product created successfully"}
    }
)
async def create_new_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, product)

@app.put(
    "/products/{product_id}",
    summary="Update an existing product",
    description="Updates the details"
        " of a specific product using its unique ID."
        " Returns the updated product details.",
    response_model=ProductOut,
    responses={
        200: {"description": "Product updated successfully"},
        404: {"description": "Product not found"}
    }
)
async def update_existing_product(product_id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    updated_product = await update_product(db, product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@app.delete(
    "/products/{product_id}",
    summary="Delete a specific product",
    description="Deletes a specific product using its unique ID."
        " Returns the details of the deleted product.",
    response_model=ProductOut,
    responses={
        200: {"description": "Product deleted successfully"},
        404: {"description": "Product not found"}
    }
)
async def delete_existing_product(product_id: int, db: AsyncSession = Depends(get_db)):
    deleted_product = await delete_product(db, product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product


@app.post(
    "/purchase",
    summary="Make a product purchase",
    description=(
        "Handles the purchase of a specific product from a specific location."
        " Reduces the product stock based on the purchase quantity."
        " If the stock falls below 100, an order is created for restocking."
    ),
    responses={
        200: {"description": "Purchase processed successfully"},
        404: {"description": "Location or product not found"},
        400: {"description": "Invalid quantity or insufficient stock"}
    }
)
async def purchase_item(purchase: PurchaseRequest, db: AsyncSession = Depends(get_db)):
    return await make_purchase(
        db=db,
        location_id=purchase.location_id,
        product_id=purchase.product_id,
        quantity=purchase.quantity
    )

