from fastapi import APIRouter
from uuid import UUID
from app.db.cassandra_log import CassandraEventLogger

router = APIRouter(prefix="/logs", tags=["Logs"])
event_manager = CassandraEventLogger()


@router.post("/")
def create_log(user_id: str, event_type: str, metadata: str):
    event_id = event_manager.create_log(user_id, event_type, metadata)
    return {"event_id": str(event_id)}


@router.get("/")
def get_logs(event_type: str, hours: int = 24):
    return event_manager.get_recent_events_by_type(event_type, hours)


@router.put("/{event_id}")
def update_log(event_id: UUID, metadata: str):
    event_manager.update_metadata(event_id, metadata)
    return {"detail": "Metadata updated"}


@router.delete("/old")
def delete_old_logs(days: int = 7):
    count = event_manager.delete_old_logs(days)
    return {"deleted": count}
