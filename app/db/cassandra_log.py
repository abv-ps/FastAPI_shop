import asyncio
import uuid
import logging
from datetime import datetime, timedelta, timezone
from cassandra.cluster import Cluster
from cassandra.query import dict_factory

from app.utils import cassandra_commands as CQL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class CassandraEventLogger:
    def __init__(self,
                 host: str = "cassandra",
                 keyspace: str = "eventlog",
                 default_ttl: int = 86400
                 ):
        self.cluster = Cluster([host])
        self.session = self.cluster.connect(keyspace)
        self.session.row_factory = dict_factory
        self.default_ttl = default_ttl

    def create_log(self,
                   user_id: str,
                   event_type: str,
                   metadata: str,
                   ttl: int | None = None
                   ):
        event_id = uuid.uuid4()
        timestamp = datetime.now(timezone.utc)
        try:
            effective_ttl = ttl if ttl is not None else self.default_ttl
            self.session.execute(CQL.INSERT_LOG, (event_id,
                                                  user_id,
                                                  event_type,
                                                  timestamp,
                                                  metadata,
                                                  effective_ttl))
            logger.info(f"Created log for user {user_id} with event {event_type}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to create log: {e}")
            raise

    async def create_log_async(self,
                               user_id: str,
                               event_type: str,
                               metadata: str,
                               ttl: int | None = None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.create_log(user_id, event_type, metadata, ttl)
        )

    def get_recent_events_by_type(self, event_type: str, hours: int = 24):
        time_limit = datetime.now(timezone.utc) - timedelta(hours=hours)
        rows = self.session.execute(CQL.SELECT_RECENT_EVENTS, (event_type, time_limit))
        return list(rows)

    def update_metadata(self, event_id: uuid.UUID, new_metadata: str):
        try:
            self.session.execute(CQL.UPDATE_METADATA, (new_metadata, event_id))
            logger.info(f"Updated metadata for event {event_id}")
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            raise

    def delete_old_logs(self, days: int = 7):
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        rows = self.session.execute(CQL.SELECT_ALL_LOGS)
        deleted = 0
        for row in rows:
            if row["timestamp"] < threshold:
                self.session.execute(CQL.DELETE_LOG, (row["event_id"],))
                deleted += 1
        logger.info(f"Deleted {deleted} old logs")
        return deleted
