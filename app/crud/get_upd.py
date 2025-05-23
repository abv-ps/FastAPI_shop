from bson import ObjectId, errors
from fastapi import HTTPException
from app.db.database import db
from app.db.cassandra_log import CassandraEventLogger
import json

event_logger = CassandraEventLogger()

async def get_recent_orders(user_id: str = "anonymous"):
    orders = await db.orders.find().sort("date", -1).limit(100).to_list(length=100)
    for o in orders:
        o["id"] = str(o["_id"])
        o.pop("_id")

    await event_logger.create_log_async(
        user_id=user_id,
        event_type="view_orders",
        metadata=json.dumps({"count": len(orders)})
    )

    return orders

async def update_stock(product_id: str, quantity: int, user_id: str = "anonymous"):
    try:
        obj_id = ObjectId(product_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    result = await db.products.update_one(
        {"_id": obj_id},
        {"$inc": {"stock": -quantity}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    await event_logger.create_log_async(
        user_id=user_id,
        event_type="update_stock",
        metadata=json.dumps({
            "product_id": product_id,
            "quantity_delta": -quantity
        })
    )

    return {"updated": result.modified_count}
