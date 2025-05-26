"""
Session management API router module.

This module provides endpoints for managing user sessions,
including creating, deleting, retrieving, and updating sessions,
as well as fetching user ID by session token.

Endpoints:
- POST /session/{user_id} : Start a session for a given user ID.
- DELETE /session/{user_id} : End a session for a given user ID.
- GET /session/{user_id} : Retrieve session information for a user.
- PUT /session/{user_id} : Update session activity timestamp for a user.
- GET /session/by-token/ : Retrieve user ID by session token.

Raises HTTP 404 errors when sessions or users are not found.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from app.crud.session_crud import (
    create_session,
    get_session,
    delete_session,
    update_session_activity,
    get_user_id_by_token,
)

router = APIRouter(prefix="/session", tags=["Session"])


@router.post("/{user_id}", response_model=Dict[str, Any])
async def start_session(user_id: str) -> Dict[str, Any]:
    """
    Start a session for the given user ID.

    Args:
        user_id (str): The user ID to start a session for.

    Returns:
        Dict[str, Any]: The created session data.
    """
    return await create_session(user_id)


@router.delete("/{user_id}")
async def end_session(user_id: str) -> Dict[str, str]:
    """
    End (delete) the session for the given user ID.

    Args:
        user_id (str): The user ID whose session will be deleted.

    Raises:
        HTTPException: If no session is found for the user ID.

    Returns:
        Dict[str, str]: Confirmation message of deletion.
    """
    deleted = await delete_session(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session deleted"}


@router.get("/{user_id}", response_model=Optional[Dict[str, Any]])
async def read_session(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve session data for the given user ID.

    Args:
        user_id (str): The user ID to get session data for.

    Raises:
        HTTPException: If no session is found for the user ID.

    Returns:
        Optional[Dict[str, Any]]: The session data or None.
    """
    session = await get_session(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{user_id}", response_model=Optional[Dict[str, Any]])
async def touch_session(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Update the last active time for the user's session.

    Args:
        user_id (str): The user ID whose session activity will be updated.

    Raises:
        HTTPException: If no session is found for the user ID.

    Returns:
        Optional[Dict[str, Any]]: The updated session data or None.
    """
    session = await update_session_activity(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/by-token/", response_model=Dict[str, str])
async def get_user_by_token(token: str = Query(..., description="Session token")) -> Dict[str, str]:
    """
    Retrieve user ID by session token.

    Args:
        token (str): The session token to look up.

    Raises:
        HTTPException: If no user is found for the given token.

    Returns:
        Dict[str, str]: Dictionary containing the user ID.
    """
    user_id = await get_user_id_by_token(token)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found for given token")
    return {"user_id": user_id}
