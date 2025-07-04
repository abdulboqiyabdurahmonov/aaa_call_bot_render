import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # безопаснее использовать переменную окружения
GROUP_ID = -1002344973979
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = "supersecret"  # любой строковый ключ
WEBHOOK_HOST = "https://your-render-url.onrender.com"  # замени на своё

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    fio = State()
    phone = State()
    company = State()
    tariff = State()

tariff_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Старт — 750 сум/звонок")],
        [KeyboardButton(text="💼 Бизнес — 600 сум/звонок")],
        [KeyboardButton(text="🏢 Корпоративный — 450 сум/звонок")],
        [KeyboardButton(text="🔙 Назад"), KeyboardButton(text="❌ Отменить")]
    ],
    resize_keyboard=True
)

@dp.message(F.text.lower().in_({"❌ отменить", "/отменить"}))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 Заявка отменена.", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.lower().in_({"🔙 назад", "/назад"}))
async def go_back(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current == Form.phone:
        await state.set_state(Form.fio)
        await message.answer("🔙 Введите ФИО:")
    elif current == Form.company:
        await state.set_state(Form.phone)
        await message.answer("🔙 Введите номер телефона:")
    elif current == Form.tariff:
        await state.set_state(Form.company)
        await message.answer("🔙 Введите название компании:")
    else:
        await message.answer("⏪ Назад недоступен.")

@dp.message(Form.fio)
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(Form.phone)
    await message.answer("📞 Введите номер телефона:")

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Form.company)
    await message.answer("🏢 Введите название компании:")

@dp.message(Form.company)
async def process_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(Form.tariff)
    await message.answer("📊 Выберите тариф:", reply_markup=tariff_keyboard)

@dp.message(Form.tariff)
async def process_tariff(message: types.Message, state: FSMContext):
    tariff = message.text
    await state.update_data(tariff=tariff)
    data = await state.get_data()

    text = (
        "📥 <b>Новая заявка из Telegram-бота</b>\n\n"
        f"👤 <b>ФИО:</b> {data['fio']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n"
        f"🏢 <b>Компания:</b> {data['company']}\n"
        f"📦 <b>Тариф:</b> {data['tariff']}\n"
    )

    await bot.send_message(chat_id=GROUP_ID, text=text)
    await message.answer("✅ Заявка отправлена!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@dp.message(F.command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.fio)
    await message.answer("👋 Привет! Введи, пожалуйста, своё ФИО:")

# --- Webhook setup ---
async def on_startup(bot: Bot):
    webhook_url = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url, secret_token=WEBHOOK_SECRET)

def create_app():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot, on_startup=on_startup)
    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(create_app(), port=8000)
