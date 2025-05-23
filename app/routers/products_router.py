from fastapi import APIRouter, Depends
from app.crud.crt_del import create_product, delete_unavailable_products
from app.schemas.product_schemas import ProductCreate, ProductOut
from app.dependencies.auth import get_current_user_id_optional

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductOut)
async def add_product(
    product: ProductCreate,
    user_id: str = Depends(get_current_user_id_optional)
):
    return await create_product(product.model_dump(), user_id=user_id)

@router.delete("/unavailable/")
async def delete_unavailable(user_id: str = Depends(get_current_user_id_optional)):
    return await delete_unavailable_products(user_id=user_id)
