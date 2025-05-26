"""
Product schemas module.

Defines Pydantic models for product-related data validation and serialization
used in API request and response payloads.

Models:
- ProductBase: Base model for product attributes.
- ProductCreate: Inherits ProductBase, used for product creation input.
- ProductOut: Inherits ProductBase, adds an 'id' field for output responses,
  supports ORM mode and field aliasing.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """
    Base model for product data.

    Attributes:
        name (str): Name of the product.
        price (float): Price of the product.
        category (Optional[str]): Category of the product. Defaults to None.
        description (Optional[str]): Description of the product. Defaults to None.
        stock (int): Available stock quantity.
    """

    name: str
    price: float
    category: Optional[str] = None
    description: Optional[str] = None
    stock: int


class ProductCreate(ProductBase):
    """
    Model for creating a new product.

    Inherits all fields from ProductBase.
    """
    pass


class ProductOut(ProductBase):
    """
    Model for returning product data in responses.

    Attributes:
        id (str): Unique identifier of the product.
    """

    id: str = Field(..., alias="id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
