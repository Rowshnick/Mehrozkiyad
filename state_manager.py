import aiosqlite
import json
from typing import Dict, Any
# 💡 [جدید]: برای مدیریت Serialization شیء JalaliDateTime
from persiantools.jdatetime import JalaliDateTime 

DATABASE_NAME = "user_states.db"
# وضعیت پیش‌فرض کاربر در صورتی که برای اولین بار به ربات پیام می‌دهد.
DEFAULT_STATE = {'step': 'START', 'data': {}}

def custom_json_encoder(obj):
    """
    Encoder سفارشی برای تبدیل اشیاء غیرقابل تبدیل به JSON.
    به ویژه JalaliDateTime را به رشته تبدیل می‌کند.
    """
    if isinstance(obj, JalaliDateTime):
        # تبدیل JalaliDateTime به یک رشته استاندارد (مثلاً 1400/01/01)
        return obj.strftime('%Y/%m/%d')
    
    # اگر شیء از نوع شناخته شده‌ای نبود، خطای Type پیش‌فرض را صادر کنید
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

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
                    # 💡 [نکته]: در اینجا JalaliDateTime به صورت رشته برمی‌گردد. 
                    # منطق bot_app.py باید این رشته را در صورت نیاز دوباره به JalaliDateTime تبدیل کند.
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    print(f"Error decoding state for chat_id {chat_id}. Using default state.")
                    return DEFAULT_STATE.copy()
            else:
                return DEFAULT_STATE.copy()


async def save_user_state_db(chat_id: int, state: Dict[str, Any]):
    """ذخیره یا به‌روزرسانی وضعیت کاربر در دیتابیس."""
    
    # 💡 [اصلاح]: استفاده از encoder سفارشی برای مدیریت JalaliDateTime
    state_json = json.dumps(state, default=custom_json_encoder)
    
    async with aiosqlite.connect(DATABASE_NAME) as db:
        # استفاده از UPSERT (INSERT OR REPLACE)
        await db.execute(
            """
            INSERT INTO UserStates (chat_id, state_json) VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET state_json = excluded.state_json
            """,
            (chat_id, state_json)
        )
        await db.commit()
