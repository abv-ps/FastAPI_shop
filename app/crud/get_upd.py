"""
This module provides asynchronous operations for managing and monitoring
orders and product stock levels in the system. It integrates with a MongoDB
database and logs significant actions using a Cassandra-based event logger.

Features:
- Retrieve the 100 most recent orders.
- Safely update product stock with validation.
- All user interactions are logged for auditing purposes.

Functions:
    - get_recent_orders(user_id: str = "anonymous") -> List[Dict[str, Any]]
    - update_stock(product_id: str, quantity: int, user_id: str = "anonymous") -> Dict[str, int]
"""

import json
from typing import List, Dict, Any

from bson import ObjectId, errors
from fastapi import HTTPException

from app.db.database import db
from app.db.cassandra_log import CassandraEventLogger

event_logger = CassandraEventLogger()


async def get_recent_orders(user_id: str = "anonymous") -> List[Dict[str, Any]]:
    """
    Retrieve the 100 most recent orders sorted by date in descending order.

    Args:
        user_id (str, optional): ID of the user requesting the data. Defaults to "anonymous".

    Returns:
        List[Dict[str, Any]]: A list of the most recent order documents,
                              each with a string-formatted 'id' field.
    """
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


async def update_stock(product_id: str, quantity: int, user_id: str = "anonymous") -> Dict[str, int]:
    """
    Update the stock level of a product by decreasing its quantity.

    Args:
        product_id (str): The ID of the product to update.
        quantity (int): The amount to subtract from the product's stock.
        user_id (str, optional): ID of the user performing the update. Defaults to "anonymous".

    Raises:
        HTTPException: If the product ID is invalid or the product is not found.

    Returns:
        Dict[str, int]: A dictionary indicating how many documents were updated.
    """
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
