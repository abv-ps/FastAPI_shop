from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query

from app.crud.agregate import total_spent_by_customer, sold_products_total

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/sold/")
async def sold_stats(
        start: str = Query(..., description="Start date in ISO format (e.g., 2025-01-01T00:00:00)"),
        end: str = Query(..., description="End date in ISO format (e.g., 2025-01-31T23:59:59)")
):
    try:
        start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
        end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(status_code=422,
                            detail="Invalid datetime format. Use ISO format (e.g. 2025-01-01T00:00:00)")

    return await sold_products_total(start_dt, end_dt)


@router.get("/customer/{name}")
async def customer_stats(name: str):
    return await total_spent_by_customer(name)
