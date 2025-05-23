from fastapi import APIRouter, HTTPException, Query
from app.crud.session_crud import (
    create_session,
    get_session,
    delete_session,
    update_session_activity,
    get_user_id_by_token
)

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/{user_id}")
async def start_session(user_id: str):
    return await create_session(user_id)

@router.delete("/{user_id}")
async def end_session(user_id: str):
    deleted = await delete_session(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session deleted"}

@router.get("/{user_id}")
async def read_session(user_id: str):
    session = await get_session(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{user_id}")
async def touch_session(user_id: str):
    session = await update_session_activity(user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/by-token/")
async def get_user_by_token(token: str = Query(..., description="Session token")):
    user_id = await get_user_id_by_token(token)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found for given token")
    return {"user_id": user_id}
