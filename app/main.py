from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import create_indexes
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_indexes()
    yield


app = FastAPI(
    title="Shop API",
    description="API для управління замовленнями",
    version="1.1.0",
    lifespan=lifespan
)

app.include_router(api_router)
