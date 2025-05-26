"""
Statistics API router module.

Provides endpoints to retrieve sales and customer spending statistics
over specified time intervals or by customer name.

Endpoints:
- GET /stats/sold/ : Get total sold products within a date range.
- GET /stats/customer/{name} : Get total amount spent by a specific customer.

Handles datetime parsing with ISO format and returns 422 error on invalid input.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from app.crud.aggregate import total_spent_by_customer, sold_products_total

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/sold/", response_model=Dict[str, Any])
async def sold_stats(
    start: str = Query(..., description="Start date in ISO format (e.g., 2025-01-01T00:00:00)"),
    end: str = Query(..., description="End date in ISO format (e.g., 2025-01-31T23:59:59)"),
) -> Dict[str, Any]:
    """
    Retrieve total sold products between start and end dates (inclusive).

    Args:
        start (str): Start datetime in ISO format.
        end (str): End datetime in ISO format.

    Raises:
        HTTPException: If datetime format is invalid (422 Unprocessable Entity).

    Returns:
        Dict[str, Any]: Aggregated sales statistics within the date range.
    """
    try:
        start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
        end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid datetime format. Use ISO format (e.g., 2025-01-01T00:00:00)",
        )

    return await sold_products_total(start_dt, end_dt)


@router.get("/customer/{name}", response_model=Dict[str, Any])
async def customer_stats(name: str) -> Dict[str, Any]:
    """
    Retrieve total amount spent by a customer.

    Args:
        name (str): Customer name.

    Returns:
        Dict[str, Any]: Total spending details for the customer.
    """
    return await total_spent_by_customer(name)
