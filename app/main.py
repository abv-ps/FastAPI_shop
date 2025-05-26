"""
Main application entry point for the Shop API.

This module initializes the FastAPI app with lifecycle management,
including asynchronous setup tasks such as creating database indexes.
It also includes the main API router for all endpoint registrations.

Attributes:
    app (FastAPI): The FastAPI application instance configured with metadata,
                   lifespan event handler, and included routers.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import create_indexes
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for application lifespan.

    Performs startup actions before the application starts serving requests.
    Currently ensures necessary database indexes are created.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    await create_indexes()
    yield


app = FastAPI(
    title="Shop API",
    description="API for order management",
    version="1.1.0",
    lifespan=lifespan
)

app.include_router(api_router)
