import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Настройки
API_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1002344973979"))
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://triplea-bot-web.onrender.com")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM Состояния
class Form(StatesGroup):
    fio = State()
    phone = State()
    company = State()
    tariff = State()

# Клавиатура тарифов
tariffs = {
    "Старт": "750 сум/звонок — базовый пакет с аналитикой и поддержкой",
    "Бизнес": "600 сум/звонок — расширенные функции + API доступ",
    "Корпоративный": "450 сум/звонок — полный пакет + кастомные интеграции"
}

tariff_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=name)] for name in tariffs],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Обработчики
@dp.message(F.command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.fio)
    await message.answer("👋 Привет! Введите, пожалуйста, ваше ФИО:", reply_markup=ReplyKeyboardRemove())

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

@dp.message(Form.tariff, F.text.in_(tariffs.keys()))
async def process_tariff(message: types.Message, state: FSMContext):
    choice = message.text
    await state.update_data(tariff=choice)
    data = await state.get_data()
    # Формируем сообщение
    text = (
        "📥 <b>Новая заявка из Telegram-бота</b>\n\n"
        f"👤 <b>ФИО:</b> {data['fio']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n"
        f"🏢 <b>Компания:</b> {data['company']}\n"
        f"💼 <b>Тариф:</b> {data['tariff']} — {tariffs[data['tariff']]}\n"
    )
    # Отправка в группу
    await bot.send_message(chat_id=GROUP_ID, text=text)
    await message.answer("✅ Ваша заявка отправлена! Спасибо.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(F.text.lower().in_({"отменить", "❌ отменить"}))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 Заявка отменена.", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text.lower().in_({"назад", "🔙 назад"}))
async def go_back(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current == Form.phone.state:
        await state.set_state(Form.fio)
        await message.answer("🔙 Введите ваше ФИО:")
    elif current == Form.company.state:
        await state.set_state(Form.phone)
        await message.answer("🔙 Введите номер телефона:")
    elif current == Form.tariff.state:
        await state.set_state(Form.company)
        await message.answer("🔙 Введите название компании:")
    else:
        await message.answer("⏪ Назад недоступен.")

@dp.message(F.command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Напишите /start, чтобы начать оформление заявки.")

# Webhook setup
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    await storage.close()
    await storage.wait_closed()
    logger.info("Webhook удалён, бот завершает работу.")

# Создание приложения
def create_app() -> web.Application:
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot, on_startup=on_startup, on_shutdown=on_shutdown)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
