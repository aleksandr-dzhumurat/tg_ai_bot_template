import time

import aiosqlite

from .config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                username TEXT,
                channel TEXT,
                role TEXT NOT NULL,
                message_text TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)
        for col, col_type in [("username", "TEXT"), ("channel", "TEXT")]:
            try:
                await db.execute(f"ALTER TABLE messages ADD COLUMN {col} {col_type}")
            except aiosqlite.OperationalError:
                pass  # column already exists
        await db.commit()


async def save_message(chat_id: str, username: str | None, role: str, message_text: str, channel: str | None = None):
    """role: 'user' or 'assistant'"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (chat_id, username, channel, role, message_text, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, username, channel, role, message_text, int(time.time())),
        )
        await db.commit()


async def get_chat_history(chat_id: str, limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT role, message_text, username FROM messages WHERE chat_id = ? ORDER BY timestamp ASC LIMIT ?",
            (chat_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
