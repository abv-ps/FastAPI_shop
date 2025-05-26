"""
Session management module using Redis and Cassandra for audit logging.

This module defines the SessionManager class, which handles user session
lifecycle operations such as session creation, deletion, activity updates,
and retrieval. Redis is used for fast in-memory session storage, while
Cassandra logs provide persistent audit trails of session events.

Usage:
    session_manager = SessionManager()
    await session_manager.create("user_id")
    await session_manager.get("user_id")
    await session_manager.delete("user_id")
"""

import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from redis.asyncio import Redis

from app.db.cassandra_log import CassandraEventLogger

event_logger = CassandraEventLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user sessions using Redis for storage and Cassandra for logging.

    Provides asynchronous methods to create, delete, update, and retrieve
    session data in a scalable and observable way.
    """

    def __init__(self, host: str = "redis", port: int = 6379, ttl: int = 1800) -> None:
        """
        Initialize the session manager.

        Args:
            host (str): Redis host.
            port (int): Redis port.
            ttl (int): Default time-to-live (in seconds) for a session.
        """
        self.redis: Redis = Redis(host=host, port=port, decode_responses=True)
        self.ttl: int = ttl

    def _session_key(self, user_id: str) -> str:
        return f"session:{user_id}"

    def _token_key(self, token: str) -> str:
        return f"token:{token}"

    async def create(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new session for a user.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            Dict[str, Any]: The session data containing user_id, token, login time, etc.
        """
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
        """
        Delete an existing session by user ID.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            int: Number of keys deleted (0 or 1).
        """
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

    async def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data for a given user.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            Optional[Dict[str, Any]]: Session data or None if not found.
        """
        logger.debug(f"Fetching session for user {user_id}")
        data = await self.redis.get(self._session_key(user_id))
        return json.loads(data) if data else None

    async def get_user_id_by_token(self, token: str) -> Optional[str]:
        """
        Retrieve the user ID associated with a session token.

        Args:
            token (str): The session token.

        Returns:
            Optional[str]: The user ID or None if not found.
        """
        logger.debug(f"Fetching user_id by token {token}")
        return await self.redis.get(self._token_key(token))

    async def touch(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Refresh the session's TTL and update the last active timestamp.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            Optional[Dict[str, Any]]: The updated session data or None if not found.
        """
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

    async def close(self) -> None:
        """
        Close the Redis connection.
        """
        await self.redis.close()
