"""Show recent messages from the SQLite message store (most recent first)."""
import asyncio
import os
import sys

import aiosqlite

sys.path.insert(0, "/srv")
from src.config import DB_PATH

LIMIT = int(os.environ.get("HISTORY_LIMIT", "50"))


async def main():
    if not os.path.exists(DB_PATH):
        print(f"No database found at {DB_PATH}")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT chat_id, username, channel, role, message_text, datetime(timestamp, 'unixepoch') AS ts
            FROM messages
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (LIMIT,),
        ) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        print("No messages yet.")
        return

    print(f"{'TIME':<20} {'USERNAME':<25} {'CHANNEL':<20} {'ROLE':<10} MESSAGE")
    print("-" * 120)
    for row in rows:
        msg = row["message_text"].replace("\n", " ")
        if len(msg) > 60:
            msg = msg[:57] + "..."
        username = row["username"] or row["chat_id"]
        channel = row["channel"] or "-"
        print(f"{row['ts']:<20} {username:<25} {channel:<20} {row['role']:<10} {msg}")


if __name__ == "__main__":
    asyncio.run(main())
