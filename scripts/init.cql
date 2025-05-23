CREATE KEYSPACE IF NOT EXISTS eventlog
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

USE eventlog;

CREATE TABLE IF NOT EXISTS logs (
    event_id UUID PRIMARY KEY,
    user_id TEXT,
    event_type TEXT,
    timestamp TIMESTAMP,
    metadata TEXT
);
