from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Header, Depends


from app.dependencies.auth import get_current_user_id_optional
from app.schemas.orders_schemas import OrderOut, OrderCreate
from app.crud.crt_del import create_order
from app.crud.get_upd import get_recent_orders, update_stock

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
async def add_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id_optional)
):
    for item in order.items:
        await update_stock(item.product_id, item.quantity, user_id=user_id)
    return await create_order(order.model_dump(), background_tasks, user_id)


@router.get("/recent/", response_model=List[OrderOut])
async def recent_orders(user_id: str = Depends(get_current_user_id_optional)):
    return await get_recent_orders(user_id=user_id)