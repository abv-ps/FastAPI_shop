from app.db.redis_session import SessionManager

session_manager = SessionManager()

create_session = session_manager.create
delete_session = session_manager.delete
get_session = session_manager.get
update_session_activity = session_manager.touch
get_user_id_by_token = session_manager.get_user_id_by_token
