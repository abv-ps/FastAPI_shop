import json
import logging
import secrets
from redis.asyncio import Redis
from datetime import datetime, timezone
from app.db.cassandra_log import CassandraEventLogger

event_logger = CassandraEventLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, host='redis', port=6379, ttl=1800):
        self.redis = Redis(host=host, port=port, decode_responses=True)
        self.ttl = ttl

    def _session_key(self, user_id: str) -> str:
        return f"session:{user_id}"

    def _token_key(self, token: str) -> str:
        return f"token:{token}"

    async def create(self, user_id: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        session_token = secrets.token_hex(16)
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "login_time": now,
            "last_active": now
        }
        try:
            logger.info(f"Creating new session for user {user_id}")
            await self.redis.setex(
                self._session_key(user_id),
                self.ttl,
                json.dumps(session_data)
            )
            await self.redis.setex(
                self._token_key(session_token),
                self.ttl,
                user_id
            )

            await event_logger.create_log_async(
                user_id=user_id,
                event_type="login",
                metadata=json.dumps({"session_token": session_token})
            )

        except Exception as e:
            logger.error(f"Session error for user {user_id}: {e}")
            raise
        finally:
            logger.debug(f"Session created for user {user_id}")
        return session_data

    async def delete(self, user_id: str) -> int:
        session = await self.get(user_id)
        if not session:
            logger.warning(f"Session not found for user {user_id} to delete")
            return 0
        token = session.get("session_token")
        try:
            deleted_count = await self.redis.delete(self._session_key(user_id))
            if token:
                await self.redis.delete(self._token_key(token))
            logger.info(f"Deleted session for user {user_id}")

            await event_logger.create_log_async(
                user_id=user_id,
                event_type="logout",
                metadata=json.dumps({"deleted_session": True})
            )

            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting session for user {user_id}: {e}")
            raise

    async def get(self, user_id: str) -> dict | None:
        logger.debug(f"Fetching session for user {user_id}")
        data = await self.redis.get(self._session_key(user_id))
        return json.loads(data) if data else None

    async def get_user_id_by_token(self, token: str) -> str | None:
        logger.debug(f"Fetching user_id by token {token}")
        user_id = await self.redis.get(self._token_key(token))
        return user_id

    async def touch(self, user_id: str) -> dict | None:
        session = await self.get(user_id)
        if session:
            try:
                session["last_active"] = datetime.now(timezone.utc).isoformat()
                await self.redis.setex(self._session_key(user_id), self.ttl, json.dumps(session))
                await self.redis.setex(self._token_key(session["session_token"]), self.ttl, user_id)
                logger.info(f"Updated session activity for user {user_id}")

                await event_logger.create_log_async(
                    user_id=user_id,
                    event_type="activity_touch",
                    metadata=json.dumps({"status": "touched"})
                )

            except Exception as e:
                logger.error(f"Session error for user {user_id}: {e}")
                raise
        return session

    async def close(self):
        await self.redis.close()
