from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "callback_query" in data:
        chat_id = data["callback_query"]["from"]["id"]
        text = data["callback_query"]["data"]
        await send_message(chat_id, f"Вы нажали: {text}")
        return {"ok": True}

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            await send_buttons(chat_id)
        else:
            await send_message(chat_id, "Нажмите /start, чтобы начать.")
    return {"ok": True}

async def send_buttons(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Оставить заявку", "callback_data": "Заявка"}],
            [{"text": "Связаться с менеджером", "callback_data": "Менеджер"}]
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Что вы хотите сделать?",
            "reply_markup": keyboard
        })

async def send_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })

@app.get("/")
def root():
    return {"status": "ok"}
