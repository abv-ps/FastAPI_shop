INSERT_LOG = """
    INSERT INTO logs (event_id, user_id, event_type, timestamp, metadata)
    VALUES (%s, %s, %s, %s, %s) USING TTL %s
"""

SELECT_RECENT_EVENTS = """
    SELECT * FROM logs
    WHERE event_type=%s AND timestamp > %s ALLOW FILTERING
"""

UPDATE_METADATA = """
    UPDATE logs SET metadata = %s WHERE event_id = %s
"""

SELECT_ALL_LOGS = """
    SELECT event_id, timestamp FROM logs
"""

DELETE_LOG = """
    DELETE FROM logs WHERE event_id = %s
"""
