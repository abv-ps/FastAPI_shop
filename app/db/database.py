"""
This module sets up the MongoDB connection using Motor (an async MongoDB driver)
and provides an asynchronous function to initialize database indexes.

It is intended to be imported early in the application lifecycle to ensure
that indexes are created and available for use by MongoDB queries.

Exposed components:
    - `db`: The MongoDB database client for the "shop" database.
    - `create_indexes()`: Initializes required indexes on collections.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase


client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://mongo:27017")
db: AsyncIOMotorDatabase = client["shop"]


async def create_indexes() -> None:
    """
    Create indexes on collections to improve query performance.

    Specifically, this function creates an index on the 'category' field 
    in the 'products' collection.

    Returns:
        None
    """
    await db.products.create_index("category")
