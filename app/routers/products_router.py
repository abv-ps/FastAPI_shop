"""
Products API router module.

This module defines API endpoints for product-related operations, including
creating new products and deleting products that are unavailable (out of stock).
Endpoints are secured optionally by user session tokens.

Endpoints:
- POST /products/ : Create a new product.
- DELETE /products/unavailable/ : Delete all unavailable products.

Dependencies:
- get_current_user_id_optional: Retrieves current user ID from session token or defaults to "anonymous".
"""

from fastapi import APIRouter, Depends
from app.crud.crt_del import create_product, delete_unavailable_products
from app.schemas.product_schemas import ProductCreate, ProductOut
from app.dependencies.auth import get_current_user_id_optional

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductOut)
async def add_product(
    product: ProductCreate,
    user_id: str = Depends(get_current_user_id_optional),
) -> ProductOut:
    """
    Create a new product entry.

    Args:
        product (ProductCreate): Product data for creation.
        user_id (str): ID of the user performing the operation, defaults to "anonymous".

    Returns:
        ProductOut: The created product data.
    """
    product_data = product.model_dump()
    created_product = await create_product(product_data, user_id=user_id)
    return ProductOut(**created_product)


@router.delete("/unavailable/")
async def delete_unavailable(
    user_id: str = Depends(get_current_user_id_optional),
) -> dict[str, int]:
    """
    Delete all products that are currently unavailable (stock == 0).

    Args:
        user_id (str): ID of the user performing the operation, defaults to "anonymous".

    Returns:
        dict[str, int]: Dictionary with count of deleted products.
    """
    return await delete_unavailable_products(user_id=user_id)
