from fastapi import APIRouter
from app.routers.cassandra_logs import router as logs_router
from app.routers.products_router import router as products_router
from app.routers.orders_router import router as orders_router
from app.routers.sessions_router import router as sessions_router

api_router = APIRouter()
api_router.include_router(logs_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(sessions_router)
