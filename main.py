import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    phone = State()
    company = State()
    tariff = State()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="Связаться с менеджером")]
    ],
    resize_keyboard=True
)

tariff_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Старт (750 сум/звонок)")],
        [KeyboardButton(text="Бизнес (600 сум/звонок)")],
        [KeyboardButton(text="Корпоративный (450 сум/звонок до 100 000 звонков)")]
    ],
    resize_keyboard=True
)

@dp.message(commands=["start", "отменить", "назад"])
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)

@dp.message(lambda msg: msg.text == "Оставить заявку")
async def start_form(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше ФИО:")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите название компании:")
    await state.set_state(Form.company)

@dp.message(Form.company)
async def get_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer("Выберите тариф:", reply_markup=tariff_keyboard)
    await state.set_state(Form.tariff)

@dp.message(Form.tariff)
async def get_tariff(message: types.Message, state: FSMContext):
    await state.update_data(tariff=message.text)
    data = await state.get_data()
    text = (
        "<b>Заявка из Telegram-бота</b>\n\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Телефон:</b> {data['phone']}\n"
        f"<b>Компания:</b> {data['company']}\n"
        f"<b>Тариф:</b> {data['tariff']}"
    )
    await bot.send_message(chat_id=GROUP_ID, text=text)
    await message.answer("Спасибо! Ваша заявка отправлена!", reply_markup=keyboard)
    await state.clear()

@dp.message(lambda msg: msg.text == "Связаться с менеджером")
async def contact_manager(message: types.Message):
    await message.answer("Менеджер свяжется с вами в ближайшее время.")

async def on_startup(app):
    await bot.set_webhook("https://triplea-bot-web.onrender.com/webhook")

app = web.Application()
dp.include_router(dp)
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
app.on_startup.append(on_startup)

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    web.run_app(app, port=8080)
