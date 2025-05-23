from typing import List

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderBase(BaseModel):
    customer: str
    items: List[OrderItem]
    total: float

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: str = Field(..., alias="id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True