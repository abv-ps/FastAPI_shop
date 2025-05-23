from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    price: float
    category: Optional[str] = None
    description: Optional[str] = None
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: str = Field(..., alias="id")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


