from datetime import datetime
from backend.database.database import connect

def record(level: str, message: str) -> None:
    with connect() as db:
        db.execute("INSERT INTO logs(timestamp, level, message) VALUES(?,?,?)", (datetime.now().isoformat(timespec="seconds"), level, message))

def recent(level: str | None = None) -> list[dict]:
    with connect() as db:
        rows = db.execute("SELECT * FROM logs WHERE (? IS NULL OR level=?) ORDER BY id DESC LIMIT 500", (level, level)).fetchall()
    return [dict(row) for row in reversed(rows)]

def clear() -> None:
    with connect() as db:
        db.execute("DELETE FROM logs")
