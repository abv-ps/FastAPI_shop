"""
Order schemas module.

Defines Pydantic models for order-related data validation and serialization
used in request and response bodies for API endpoints.

Models:
- OrderItem: Represents a single item in an order.
- OrderBase: Base model for order containing customer info, items, and total price.
- OrderCreate: Inherits OrderBase, used for creating new orders.
- OrderOut: Inherits OrderBase with an added `id` field for output responses,
  supports ORM mode and field aliasing.
"""

from typing import List

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """
    Represents a single product item in an order.

    Attributes:
        product_id (str): The ID of the product.
        quantity (int): The quantity of the product ordered.
    """

    product_id: str
    quantity: int


class OrderBase(BaseModel):
    """
    Base model for order data.

    Attributes:
        customer (str): Name or identifier of the customer.
        items (List[OrderItem]): List of items included in the order.
        total (float): Total price for the order.
    """

    customer: str
    items: List[OrderItem]
    total: float


class OrderCreate(OrderBase):
    """
    Model used when creating a new order.

    Inherits all fields from OrderBase.
    """
    pass


class OrderOut(OrderBase):
    """
    Model used when returning order data in responses.

    Attributes:
        id (str): Unique identifier of the order.
    """

    id: str = Field(..., alias="id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
