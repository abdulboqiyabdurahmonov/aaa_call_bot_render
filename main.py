from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Простая память (слетает при перезапуске, но норм для старта)
user_states = {}
user_data = {}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            await send_message(chat_id, "Привет! Давайте оформим заявку.\n\nКак вас зовут?")
            user_states[chat_id] = "waiting_name"
            user_data[chat_id] = {}
        else:
            await handle_step(chat_id, text)

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        tariff = callback["data"]
        user_data[chat_id]["tariff"] = tariff
        await send_message(chat_id, "Спасибо! Ваша заявка отправлена ✅")

        # Отправка заявки в группу
        msg = format_application(user_data[chat_id])
        await send_message(GROUP_ID, msg)

        # Очистка состояния
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    return {"ok": True}

async def handle_step(chat_id, text):
    state = user_states.get(chat_id)

    if state == "waiting_name":
        user_data[chat_id]["name"] = text
        user_states[chat_id] = "waiting_phone"
        await send_message(chat_id, "Введите номер телефона:")
    elif state == "waiting_phone":
        user_data[chat_id]["phone"] = text
        user_states[chat_id] = "waiting_company"
        await send_message(chat_id, "Введите название вашей компании:")
    elif state == "waiting_company":
        user_data[chat_id]["company"] = text
        user_states[chat_id] = "waiting_tariff"
        await send_tariff_buttons(chat_id)
    else:
        await send_message(chat_id, "Нажмите /start, чтобы начать заново.")

async def send_tariff_buttons(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🟢 Старт", "callback_data": "Старт"}],
            [{"text": "🔵 Бизнес", "callback_data": "Бизнес"}],
            [{"text": "🔴 Корпоративный", "callback_data": "Корпоративный"}]
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "Выберите интересующий тариф:",
            "reply_markup": keyboard
        })

def format_application(data):
    return (
        "📥 *Новая заявка*\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"🏢 Компания: {data.get('company')}\n"
        f"📦 Тариф: {data.get('tariff')}"
    )

async def send_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })

@app.get("/")
def root():
    return {"status": "ok"}
