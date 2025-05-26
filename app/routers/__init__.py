"""
This module configures the main API router by aggregating sub-routers
for different resource domains such as Cassandra logs, products, orders,
and sessions.

It serves as a centralized point to include all route handlers
and organize the API endpoints logically within the FastAPI application.
"""

from fastapi import APIRouter
from app.routers.cassandra_logs import router as logs_router
from app.routers.products_router import router as products_router
from app.routers.orders_router import router as orders_router
from app.routers.sessions_router import router as sessions_router

api_router: APIRouter = APIRouter()
api_router.include_router(logs_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(sessions_router)
