"""
This module provides a logging system for user events using Apache Cassandra
as the backend. It defines the CassandraEventLogger class for both synchronous
and asynchronous logging, metadata updates, and log cleanup operations.

Features:
- Create and store structured event logs with optional TTL (time-to-live).
- Retrieve recent events by type for analytics or debugging.
- Update event metadata post-facto.
- Remove old logs based on configurable retention.

This is intended for use in applications where persistent, high-throughput,
auditable logging is required (e.g., actions performed by users or services).
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

from app.utils import cassandra_commands as CQL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CassandraEventLogger:
    """
    A utility class for managing event logs in a Cassandra database.

    Supports synchronous and asynchronous log creation, querying recent events,
    updating metadata, and deleting outdated logs.
    """

    def __init__(
            self,
            host: str = "cassandra",
            keyspace: str = "eventlog",
            default_ttl: int = 86400
    ) -> None:
        """
        Initialize the CassandraEventLogger.

        Args:
            host (str): The Cassandra host address.
            keyspace (str): The Cassandra keyspace to use.
            default_ttl (int): Default time-to-live for logs in seconds.
        """
        self.cluster = Cluster([host])
        self.session = self.cluster.connect(keyspace)
        self.session.row_factory = dict_factory
        self.default_ttl = default_ttl

    def create_log(
            self,
            user_id: str,
            event_type: str,
            metadata: str,
            ttl: Optional[int] = None
    ) -> uuid.UUID:
        """
        Synchronously create an event log entry.

        Args:
            user_id (str): ID of the user associated with the event.
            event_type (str): The type/category of the event.
            metadata (str): Additional metadata in JSON format.
            ttl (Optional[int]): Optional TTL for the log in seconds.

        Returns:
            uuid.UUID: The unique ID of the created log entry.

        Raises:
            Exception: If log creation fails.
        """
        event_id = uuid.uuid4()
        timestamp = datetime.now(timezone.utc)
        try:
            effective_ttl = ttl if ttl is not None else self.default_ttl
            self.session.execute(
                CQL.INSERT_LOG,
                (event_id, user_id, event_type, timestamp, metadata, effective_ttl)
            )
            logger.info(f"Created log for user {user_id} with event {event_type}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to create log: {e}")
            raise

    async def create_log_async(
            self,
            user_id: str,
            event_type: str,
            metadata: str,
            ttl: Optional[int] = None
    ) -> uuid.UUID:
        """
        Asynchronously create an event log entry.

        Args:
            user_id (str): ID of the user associated with the event.
            event_type (str): The type/category of the event.
            metadata (str): Additional metadata in JSON format.
            ttl (Optional[int]): Optional TTL for the log in seconds.

        Returns:
            uuid.UUID: The unique ID of the created log entry.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.create_log(user_id, event_type, metadata, ttl)
        )

    def get_recent_events_by_type(
            self,
            event_type: str,
            hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent events of a given type within a specified time range.

        Args:
            event_type (str): The type/category of the events to retrieve.
            hours (int): The lookback period in hours.

        Returns:
            List[Dict[str, Any]]: A list of recent event logs.
        """
        time_limit = datetime.now(timezone.utc) - timedelta(hours=hours)
        rows = self.session.execute(CQL.SELECT_RECENT_EVENTS, (event_type, time_limit))
        return list(rows)

    def update_metadata(
            self,
            event_id: uuid.UUID,
            new_metadata: str
    ) -> None:
        """
        Update the metadata of a given event log.

        Args:
            event_id (uuid.UUID): The unique ID of the event log.
            new_metadata (str): New metadata in JSON format.

        Raises:
            Exception: If the update fails.
        """
        try:
            self.session.execute(CQL.UPDATE_METADATA, (new_metadata, event_id))
            logger.info(f"Updated metadata for event {event_id}")
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            raise

    def delete_old_logs(self, days: int = 7) -> int:
        """
        Delete logs older than a specified number of days.

        Args:
            days (int): The age threshold in days. Logs older than this will be deleted.

        Returns:
            int: The number of logs that were deleted.
        """
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        rows = self.session.execute(CQL.SELECT_ALL_LOGS)
        deleted = 0
        for row in rows:
            if row["timestamp"] < threshold:
                self.session.execute(CQL.DELETE_LOG, (row["event_id"],))
                deleted += 1
        logger.info(f"Deleted {deleted} old logs")
        return deleted
