"""
This module provides data aggregation functions for order-related analytics.

It includes asynchronous utility functions that interact with the MongoDB
database to perform computations such as:

- Calculating the total number of products sold within a specific date range.
- Calculating the total amount spent by a specific customer.

These functions use aggregation pipelines on the 'Orders' collection
to process and summarize data efficiently.

Functions:
    - sold_products_total(start: datetime, end: datetime) -> Dict[str, int]
    - total_spent_by_customer(customer: str) -> Dict[str, Union[int, float]]
"""
from datetime import datetime
from typing import Dict, Union

from app.db.database import db


async def sold_products_total(start: datetime, end: datetime) -> Dict[str, int]:
    """
    Calculate the total number of products sold within a given date range.

    Args:
        start (datetime): The start datetime of the range.
        end (datetime): The end datetime of the range.

    Returns:
        Dict[str, int]: A dictionary with the key 'total_sold' representing
                        the total quantity of items sold in the specified period.
    """
    pipeline = [
        {"$match": {"date": {"$gte": start, "$lte": end}}},
        {"$unwind": "$items"},
        {"$group": {"_id": None, "total_sold": {"$sum": "$items.quantity"}}}
    ]
    result = await db.orders.aggregate(pipeline).to_list(1)
    return result[0] if result else {"total_sold": 0}


async def total_spent_by_customer(customer: str) -> Dict[str, Union[int, float]]:
    """
    Calculate the total amount spent by a specific customer.

    Args:
        customer (str): The customer identifier (e.g. name or ID).

    Returns:
        Dict[str, Union[int, float]]: A dictionary with the key 'total' representing
                                      the total amount spent by the customer.
    """
    pipeline = [
        {"$match": {"customer": customer}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    result = await db.orders.aggregate(pipeline).to_list(1)
    return result[0] if result else {"total": 0}
