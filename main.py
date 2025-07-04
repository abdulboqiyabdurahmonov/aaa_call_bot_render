import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1002344973979"))

WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "supersecret"
WEBHOOK_HOST = "https://triplea-bot-web.onrender.com"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    fio = State()
    phone = State()
    company = State()
    tariff = State()

# Клавиатура тарифов с описанием
tariff_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт")],
        [KeyboardButton(text="Бизнес")],
        [KeyboardButton(text="Корпоративный")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

tariff_descriptions = {
    "Старт": "🔹 750 сум/звонок\nВключает: отчётность, аналитику, поддержку, базовые функции",
    "Бизнес": "🔸 600 сум/звонок\nВключает: отчётность, аналитику, расширенные функции, поддержку",
    "Корпоративный": "🔶 450 сум/звонок\nВключает: всё, что в Бизнес + приоритетное обслуживание и API"
}

@dp.message(F.text == "/start")
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Добро пожаловать! Введите ваше <b>ФИО</b>:")
    await state.set_state(Form.fio)

@dp.message(Form.fio)
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("📞 Введите ваш <b>номер телефона</b>:")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏢 Введите <b>название вашей компании</b>:")
    await state.set_state(Form.company)

@dp.message(Form.company)
async def process_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer("📊 Выберите <b>тариф</b>:", reply_markup=tariff_keyboard)
    await state.set_state(Form.tariff)

@dp.message(Form.tariff)
async def process_tariff(message: types.Message, state: FSMContext):
    tariff = message.text
    if tariff not in tariff_descriptions:
        await message.answer("❌ Пожалуйста, выберите тариф из списка.", reply_markup=tariff_keyboard)
        return

    await state.update_data(tariff=tariff)
    data = await state.get_data()

    text = (
        "📥 <b>Новая заявка</b>\n\n"
        f"👤 Имя: {data['fio']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🏢 Компания: {data['company']}\n"
        f"💼 Тариф: {data['tariff']}\n"
        f"ℹ️ Описание: {tariff_descriptions[tariff]}"
    )

    await bot.send_message(GROUP_ID, text)
    await message.answer("✅ Спасибо! Ваша заявка отправлена менеджеру.")
    await state.clear()

# Webhook и запуск
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)

app = web.Application()
dp.workflow_data["bot"] = bot
setup_application(app, dp, bot=bot, secret_token=WEBHOOK_SECRET)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=10000)
