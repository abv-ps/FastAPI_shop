"""
This module provides asynchronous functions for managing products and orders
in the database, including creation and cleanup operations. Each action is
logged to Cassandra for auditing purposes.

Features:
- Create new products and orders with audit logging.
- Automatically timestamp orders upon creation.
- Delete all products with zero stock and log the action.

Functions:
    - create_product(data: dict, user_id: str = "anonymous") -> dict
    - create_order(data: dict, user_id: str = "anonymous") -> dict
    - delete_unavailable_products(user_id: str = "anonymous") -> dict
"""
import orjson
import json
from datetime import datetime, timezone
from typing import Dict, Any

from app.db.database import db
from app.db.cassandra_log import CassandraEventLogger

event_logger = CassandraEventLogger()


async def create_product(data: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
    """
    Create a new product entry in the database and log the event.

    Args:
        data (Dict[str, Any]): The product data to insert.
        user_id (str, optional): ID of the user performing the action. Defaults to "anonymous".

    Returns:
        Dict[str, Any]: The created product document with formatted ID.
    """
    result = await db.products.insert_one(data)
    created_product = await db.products.find_one({"_id": result.inserted_id})
    if created_product:
        created_product["id"] = str(created_product["_id"])
        created_product.pop("_id")

        await event_logger.create_log_async(
            user_id=user_id,
            event_type="create_product",
            metadata=json.dumps({
                "product_id": created_product["id"],
                "name": created_product.get("name")
            })
        )

    return created_product


async def create_order(data: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
    """
    Create a new order entry with a UTC timestamp and log the event.

    Args:
        data (Dict[str, Any]): The order data to insert.
        user_id (str, optional): ID of the user performing the action. Defaults to "anonymous".

    Returns:
        Dict[str, Any]: The created order document with formatted ID.
    """
    data["date"] = datetime.now(timezone.utc)
    result = await db.orders.insert_one(data)
    order = await db.orders.find_one({"_id": result.inserted_id})

    order["id"] = str(order["_id"])
    order.pop("_id")

    metadata_json = orjson.dumps(order).decode()

    await event_logger.create_log_async(
        user_id=user_id,
        event_type="order_created",
        metadata=metadata_json
    )

    return order


async def delete_unavailable_products(user_id: str = "anonymous") -> Dict[str, int]:
    """
    Delete all products with zero stock and log the deletion event.

    Args:
        user_id (str, optional): ID of the user performing the action. Defaults to "anonymous".

    Returns:
        Dict[str, int]: A dictionary containing the number of deleted products.
    """
    result = await db.products.delete_many({"stock": 0})

    await event_logger.create_log_async(
        user_id=user_id,
        event_type="delete_unavailable_products",
        metadata=json.dumps({"deleted_count": result.deleted_count})
    )

    return {"deleted_count": result.deleted_count}
