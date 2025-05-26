"""
This module defines API routes for managing orders within the application.

It provides endpoints to create new orders and to retrieve recent orders.
User identification is handled optionally via a dependency that extracts
the user ID from session tokens or returns "anonymous" if unavailable.

Stock levels are updated asynchronously in the background when orders are created.
"""

from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends

from app.dependencies.auth import get_current_user_id_optional
from app.schemas.orders_schemas import OrderOut, OrderCreate
from app.crud.crt_del import create_order
from app.crud.get_upd import get_recent_orders, update_stock

router: APIRouter = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut)
async def add_order(
    order: OrderCreate,
    user_id: str = Depends(get_current_user_id_optional),
) -> OrderOut:
    """
    Create a new order and update stock quantities for ordered items.

    Args:
        order (OrderCreate): The order data to create.
        background_tasks (BackgroundTasks): FastAPI background tasks handler.
        user_id (str): The ID of the user placing the order, optional.

    Returns:
        OrderOut: The created order details.
    """
    for item in order.items:
        await update_stock(item.product_id, item.quantity, user_id=user_id)
        order_dict = await create_order(order.model_dump(), user_id=user_id)
    return OrderOut(**order_dict)


@router.get("/recent/", response_model=List[OrderOut])
async def recent_orders(user_id: str = Depends(get_current_user_id_optional)) -> List[OrderOut]:
    """
    Retrieve a list of recent orders.

    Args:
        user_id (str): The ID of the user requesting recent orders, optional.

    Returns:
        List[OrderOut]: A list of recent orders.
    """
    orders_data = await get_recent_orders(user_id=user_id)
    return [OrderOut(**order) for order in orders_data]

