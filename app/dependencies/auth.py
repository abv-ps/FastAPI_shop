"""
This module defines FastAPI dependency functions for retrieving the 
current user's ID based on a session token passed in the request header.

It supports optional authentication and defaults to returning "anonymous"
if no valid session token is provided.

Intended for routes where both authenticated and anonymous access are allowed.
"""

from fastapi import Header
from typing import Optional
from app.crud.session_crud import get_user_id_by_token


async def get_current_user_id_optional(
    session_token: Optional[str] = Header(default=None)
) -> str:
    """
    Dependency function to retrieve the current user's ID based on a session token.

    If the session token is not present or invalid, it returns "anonymous".

    Args:
        session_token (Optional[str]): The session token from the request headers.

    Returns:
        str: The user ID associated with the session, or "anonymous" if not found.
    """
    if not session_token:
        return "anonymous"

    user_id = await get_user_id_by_token(session_token)
    return user_id if user_id else "anonymous"
