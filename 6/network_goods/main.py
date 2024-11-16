import json
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException


app = FastAPI()

@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    with open("openapi.json", 'w') as fin:
        json.dump(openapi_data, fin)


class Item(BaseModel):
    """
    Represents an item available in the inventory.

    Attributes:
    - id: Unique identifier for the item (str).
    - name: Name of the item (str).
    - description: (Optional) A description of the item (str).
    - min_quantity: The minimum quantity required to avoid stockouts (int).
    - max_quantity: The maximum quantity that can be stored for the item (int).
    """
    id: str
    name: str
    description: Optional[str] = None
    min_quantity: int
    max_quantity: int


items_db: Dict[str, Item] = {}


class Location(BaseModel):
    """
    Represents a storage location within the inventory system.

    Attributes:
    - id: Unique identifier for the location (int).
    - name: Name of the location (str).
    - location: Physical address or description of the location (str).
    - inventory: A dictionary mapping item IDs to their quantities at this location (Dict[str, int]).
    """
    id: int
    name: str
    location: str
    inventory: Dict[str, int] = {}


locations_db: List[Location] = []


class Purchase(BaseModel):
    """
    Represents a purchase transaction for an item.

    Attributes:
    - item_id: Unique identifier for the item being purchased (str).
    - quantity: The quantity of the item being purchased (int).
    """
    item_id: str
    quantity: int


purchases_db: List[Purchase] = []


class UpdateInventoryRequest(BaseModel):
    """
    Represents a request to update the inventory for an item.

    Attributes:
    - item_id: Unique identifier for the item whose inventory is being updated (str).
    - quantity_change: The change in quantity for the item (int).
    """
    item_id: str
    quantity_change: int


# --- CRUD operation for Location ---

@app.post("/locations/", response_model=Location)
async def create_location(location: Location):
    """
    Creates a new location in the system.
    
    Parameters:
    - **location**: An object containing the location ID, name, and type.

    Returns:
    - The newly created Location object.
    """
    locations_db.append(location)
    return location


@app.get("/locations/", response_model=List[Location])
async def get_locations():
    """
    Retrieves a list of all locations in the system.
    
    Returns:
    - A list of Location objects, each representing a different location.
    """
    return locations_db


@app.get("/locations/{location_id}", response_model=Location)
async def get_location(location_id: int):
    """
    Retrieves information about a specific location by its ID.
    
    Parameters:
    - **location_id**: The unique identifier for the requested location.

    Returns:
    - The Location object corresponding to the specified ID.

    Raises:
    - HTTPException: If the location is not found (404).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

# --- CRUD operation for Item ---

# Получение списка всех товаров
@app.get("/items/", response_model=List[Item])
async def get_items():
    """
    Retrieves a list of all items in the system.
    
    Returns:
    - A list of Item objects, each representing a different item.
    """
    return list(items_db.values())

# --- Work with Item in Location ---

@app.get("/locations/{location_id}/inventory/", response_model=Dict[str, int])
async def get_inventory(location_id: int):
    """
    Retrieves the inventory of items for a specific location.
    
    Parameters:
    - **location_id**: The unique identifier for the location.

    Returns:
    - A dictionary mapping item IDs
        to their current quantities in the specified location.

    Raises:
    - HTTPException: If the location is not found (404).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location.inventory


@app.put("/locations/{location_id}/inventory/", response_model=Dict[str, int])
async def update_inventory(location_id: int, update_request: UpdateInventoryRequest):
    """
    Updates the quantity of an item in the specified location's inventory.
    
    Parameters:
    - **location_id**: The unique identifier for the location
        where the inventory is updated.
    - **update_request**: An object containing the item ID
        and the change in quantity.

    Returns:
    - A dictionary of the updated inventory for the specified location.

    Raises:
    - HTTPException: If the location is not found (404),
        if the item is not found (404),
        or if the resulting inventory would be negative (400).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    if update_request.item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    new_quantity = location.inventory.get(update_request.item_id, 0)
    new_quantity += update_request.quantity_change
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    
    location.inventory[update_request.item_id] = new_quantity
    return location.inventory

# --- Excess and Missing Goods ---

@app.get("/locations/{location_id}/excess_inventory/", response_model=Dict[str, int])
async def get_excess_inventory(location_id: int):
    """
    Returns items that exceed the maximum allowable quantity
    in the specified location.
    
    Parameters:
    - **location_id**: The unique identifier for the location to check.

    Returns:
    - A dictionary of item IDs that have excess inventory,
        with their quantities.
    
    Raises:
    - HTTPException: If the location is not found (404).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    excess_inventory = {}
    for item_id, quantity in location.inventory.items():
        item = items_db.get(item_id)
        if item and quantity > item.max_quantity:
            excess_inventory[item_id] = quantity
    return excess_inventory


@app.get("/locations/{location_id}/missing_inventory/", response_model=Dict[str, int])
async def get_missing_inventory(location_id: int):
    """
    Returns items that are below the minimum allowable quantity
    in the specified location.
    
    Parameters:
    - **location_id**: The unique identifier for the location to check.

    Returns:
    - A dictionary of item IDs that have missing inventory,
        with their quantities.
    
    Raises:
    - HTTPException: If the location is not found (404).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    missing_inventory = {}
    for item_id, item in items_db.items():
        current_quantity = location.inventory.get(item_id, 0)
        if current_quantity < item.min_quantity:
            missing_inventory[item_id] = item.min_quantity - current_quantity
    return missing_inventory

# --- Working with purchases ---

@app.post("/locations/{location_id}/purchases/", response_model=Purchase)
async def create_purchase(location_id: int, purchase: Purchase):
    """
    Creates a purchase of an item in the specified location,
    reducing the item's quantity in inventory.
    
    Parameters:
    - **location_id**: The unique identifier for the location
        where the purchase is made.
    - **purchase**: An object containing the item ID
        and the quantity to be purchased.

    Returns:
    - The Purchase object containing the item ID and quantity purchased.

    Raises:
    - HTTPException: If the location is not found (404),
        if the item is not found (404),
        or if there is insufficient inventory
        for the requested purchase (400).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    item = items_db.get(purchase.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    current_quantity = location.inventory.get(purchase.item_id, 0)
    if current_quantity < purchase.quantity:
        raise HTTPException(status_code=400, detail="Insufficient inventory for purchase")

    location.inventory[purchase.item_id] -= purchase.quantity
    purchases_db.append(purchase)
    return purchase


@app.get("/locations/{location_id}/purchases/", response_model=List[Purchase])
async def get_purchases(location_id: int):
    """
    Retrieves all purchases for the specified location.
    
    Parameters:
    - **location_id**: The unique identifier
        for the location whose purchases are to be retrieved.

    Returns:
    - A list of Purchase objects representing all purchases made
        in the specified location.

    Raises:
    - HTTPException: If the location is not found (404).
    """
    location = next((loc for loc in locations_db if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    return [purchase for purchase in purchases_db if purchase.location_id == location_id]

