from datetime import datetime
from typing import Dict

from app.db.database import db

async def sold_products_total(start: datetime, end: datetime) -> Dict[str, int]:
    pipeline = [
        {"$match": {"date": {"$gte": start, "$lte": end}}},
        {"$unwind": "$items"},
        {"$group": {"_id": None, "total_sold": {"$sum": "$items.quantity"}}}
    ]
    result = await db.orders.aggregate(pipeline).to_list(1)
    return result[0] if result else {"total_sold": 0}

async def total_spent_by_customer(customer: str):
    pipeline = [
        {"$match": {"customer": customer}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    result = await db.orders.aggregate(pipeline).to_list(1)
    return result[0] if result else {"total": 0}