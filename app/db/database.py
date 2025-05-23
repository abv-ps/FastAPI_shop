from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://mongo:27017")
db = client["shop"]

async def create_indexes():
    await db.products.create_index("category")