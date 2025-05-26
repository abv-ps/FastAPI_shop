"""
This module defines the API routes for managing event logs using CassandraEventLogger.

It provides endpoints to create logs, retrieve recent logs by event type,
update log metadata, and delete old logs. The routes are grouped under the '/logs' prefix
and tagged as 'Logs' for documentation purposes.

All operations interact with a Cassandra backend through the CassandraEventLogger instance.
"""

from fastapi import APIRouter
from uuid import UUID
from typing import Dict, List, Any
from app.db.cassandra_log import CassandraEventLogger

router = APIRouter(prefix="/logs", tags=["Logs"])
event_manager = CassandraEventLogger()

@router.post("/", response_model=Dict[str, str])
def create_log(user_id: str, event_type: str, metadata: str) -> Dict[str, str]:
    """
    Create a new event log entry.

    Args:
        user_id (str): ID of the user creating the event.
        event_type (str): Type/category of the event.
        metadata (str): JSON string containing event metadata.

    Returns:
        Dict[str, str]: Dictionary containing the generated event ID as a string.
    """
    event_id = event_manager.create_log(user_id, event_type, metadata)
    return {"event_id": str(event_id)}


@router.get("/", response_model=List[Dict[str, Any]])
def get_logs(event_type: str, hours: int = 24) -> List[Dict[str, Any]]:
    """
    Retrieve recent event logs filtered by event type within the last specified hours.

    Args:
        event_type (str): The event type to filter logs.
        hours (int, optional): The time window in hours to look back from now. Defaults to 24.

    Returns:
        List[Dict[str, Any]]: List of event log entries as dictionaries.
    """
    return event_manager.get_recent_events_by_type(event_type, hours)


@router.put("/{event_id}", response_model=Dict[str, str])
def update_log(event_id: UUID, metadata: str) -> Dict[str, str]:
    """
    Update the metadata of an existing log entry.

    Args:
        event_id (UUID): The unique identifier of the event to update.
        metadata (str): New metadata as a JSON string.

    Returns:
        Dict[str, str]: Confirmation message of the update.
    """
    event_manager.update_metadata(event_id, metadata)
    return {"detail": "Metadata updated"}


@router.delete("/old", response_model=Dict[str, int])
def delete_old_logs(days: int = 7) -> Dict[str, int]:
    """
    Delete event logs older than a specified number of days.

    Args:
        days (int, optional): Number of days to retain logs. Logs older than this will be deleted. Defaults to 7.

    Returns:
        Dict[str, int]: Number of logs deleted.
    """
    count = event_manager.delete_old_logs(days)
    return {"deleted": count}
