# bot_app.py
import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

import utils
import keyboards
import state_manager
from handlers import astro_handlers, sajil_handlers

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await state_manager.init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            await utils.send_message(
                BOT_TOKEN,
                chat_id,
                utils.escape_markdown_v2("🌟 خوش آمدید"),
                keyboards.main_menu_keyboard()
            )
            await state_manager.save_user_state_db(chat_id, {"step": "WELCOME", "data": {}})
        else:
            state = await state_manager.get_user_state_db(chat_id)
            step = state.get("step")

            if step == "SAJIL_INPUT":
                await sajil_handlers.run_sajil_workflow(
                    chat_id, text,
                    state_manager.get_user_state_db,
                    state_manager.save_user_state_db
                )

    return {"ok": True}
