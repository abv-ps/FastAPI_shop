"""
This module provides high-level access to session management functions
by exposing a simplified interface built on top of the Redis-based
SessionManager.

It is intended to be used across the application wherever session operations
(such as creation, retrieval, deletion, or activity updates) are required.

Exposed functions:
    - create_session: Create a new session for a user.
    - delete_session: Delete an existing session by token.
    - get_session: Retrieve session data by token.
    - update_session_activity: Refresh the session's activity timestamp.
    - get_user_id_by_token: Extract the user ID from a session token.
"""

from app.db.redis_session import SessionManager

session_manager = SessionManager()

create_session = session_manager.create

delete_session = session_manager.delete

get_session = session_manager.get

update_session_activity = session_manager.touch

get_user_id_by_token = session_manager.get_user_id_by_token
