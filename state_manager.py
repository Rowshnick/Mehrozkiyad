import aiosqlite
import json
from typing import Dict, Any

DATABASE_NAME = "user_states.db"
# وضعیت پیش‌فرض کاربر در صورتی که برای اولین بار به ربات پیام می‌دهد.
DEFAULT_STATE = {'step': 'START', 'data': {}}

async def init_db():
    """ایجاد جدول UserStates در صورت عدم وجود."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS UserStates (
                chat_id INTEGER PRIMARY KEY,
                state_json TEXT NOT NULL
            )
        """)
        await db.commit()

async def get_user_state_db(chat_id: int) -> Dict[str, Any]:
    """دریافت وضعیت کاربر از دیتابیس یا بازگشت وضعیت پیش‌فرض."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute("SELECT state_json FROM UserStates WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    print(f"Error decoding state for chat_id {chat_id}. Using default state.")
                    return DEFAULT_STATE.copy()
            else:
                return DEFAULT_STATE.copy()

async def save_user_state_db(chat_id: int, state: Dict[str, Any]):
    """ذخیره یا به‌روزرسانی وضعیت کاربر در دیتابیس."""
    state_json = json.dumps(state)
    async with aiosqlite.connect(DATABASE_NAME) as db:
        # استفاده از UPSERT (INSERT OR REPLACE)
        await db.execute(
            """
            INSERT INTO UserStates (chat_id, state_json) VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET state_json = ?
            """,
            (chat_id, state_json, state_json)
        )
        await db.commit()
