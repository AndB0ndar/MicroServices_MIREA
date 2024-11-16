from pydantic import BaseModel
from typing import Optional, List


class LocationBase(BaseModel):
    """
    Base schema for a location.
    Fields:
        - name: Name of the location.
        - address: Address of the location.
    """
    name: str
    address: str
    products: List[int] = []

class LocationCreate(LocationBase):
    """
    Schema for creating a new location.
    Inherits all fields from LocationBase.
    """
    pass

class LocationUpdate(LocationBase):
    """
    Schema for updating an existing location.
    Inherits all fields from LocationBase.
    """
    pass

class LocationOut(LocationBase):
    """
    Schema for outputting location details.
    Fields:
        - id: Unique identifier of the location.
        - products: List of associated product IDs.
    """
    id: int

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    """
    Base schema for a product.
    Fields:
        - name: Name of the product.
        - description: Optional description of the product.
        - price: Price of the product.
        - stock: Quantity of the product in stock.
    """
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    """
    Schema for creating a new product.
    Inherits all fields from ProductBase.
    """
    pass

class ProductUpdate(ProductBase):
    """
    Schema for updating an existing product.
    Inherits all fields from ProductBase.
    """
    pass

class ProductOut(ProductBase):
    """
    Schema for outputting product details.
    Fields:
        - id: Unique identifier of the product.
    """
    id: int

    class Config:
        orm_mode = True


class PurchaseRequest(BaseModel):
    """
    Schema for a purchase request.
    Fields:
        - location_id: ID of the location where the purchase is made.
        - product_id: ID of the product being purchased.
        - stock: Quantity of the product being purchased.
    """
    location_id: int
    product_id: int
    stock: int

