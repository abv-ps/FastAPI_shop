from fastapi import Header
from typing import Optional
from app.crud.session_crud import get_user_id_by_token

async def get_current_user_id_optional(session_token: Optional[str] = Header(None)) -> str:
    if not session_token:
        return "anonymous"

    user_id = await get_user_id_by_token(session_token)
    return user_id if user_id else "anonymous"