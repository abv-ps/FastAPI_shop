import json
from fastapi import BackgroundTasks
from datetime import datetime, timezone
from app.db.database import db
from app.db.cassandra_log import CassandraEventLogger

event_logger = CassandraEventLogger()

async def create_product(data: dict, user_id: str = "anonymous"):
    result = await db.products.insert_one(data)
    created_product = await db.products.find_one({"_id": result.inserted_id})
    if created_product:
        created_product["id"] = str(created_product["_id"])
        created_product.pop("_id")

        await event_logger.create_log_async(
            user_id=user_id,
            event_type="create_product",
            metadata=json.dumps({"product_id": created_product["id"], "name": created_product.get("name")})
        )

    return created_product


async def create_order(data: dict, user_id: str = "anonymous"):
    data["date"] = datetime.now(timezone.utc)
    result = await db.orders.insert_one(data)
    order = await db.orders.find_one({"_id": result.inserted_id})

    order["id"] = str(order["_id"])
    order.pop("_id")

    metadata_json = json.dumps(order)

    await event_logger.create_log_async(
        user_id=user_id,
        event_type="order_created",
        metadata=metadata_json
    )

    return order


async def delete_unavailable_products(user_id: str = "anonymous"):
    result = await db.products.delete_many({"stock": 0})

    await event_logger.create_log_async(
        user_id=user_id,
        event_type="delete_unavailable_products",
        metadata=json.dumps({"deleted_count": result.deleted_count})
    )

    return {"deleted_count": result.deleted_count}
