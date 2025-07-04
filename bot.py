import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, CommandStart

API_TOKEN = '7993696802:AAHsaOyLkComr4mr2WsC-EgnB5jcHKjd7Ho'
GROUP_ID = -1002344973979

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Шаги
class Form(StatesGroup):
    fio = State()
    phone = State()
    company = State()
    tariff = State()

# Кнопки тарифов
tariff_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Старт — 750 сум/звонок")],
        [KeyboardButton(text="💼 Бизнес — 600 сум/звонок")],
        [KeyboardButton(text="🏢 Корпоративный — 450 сум/звонок")],
        [KeyboardButton(text="🔙 Назад"), KeyboardButton(text="❌ Отменить")]
    ],
    resize_keyboard=True
)

# Старт
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Привет! Давай соберем твою заявку. Введи, пожалуйста, своё ФИО:")
    await state.set_state(Form.fio)

# Отмена
@dp.message(F.text.lower().in_({"❌ отменить", "/отменить"}))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 Заявка отменена.", reply_markup=types.ReplyKeyboardRemove())

# Назад
@dp.message(F.text.lower().in_({"🔙 назад", "/назад"}))
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()
    if current == Form.phone:
        await state.set_state(Form.fio)
        await message.answer("🔙 Вернулись. Введите ФИО:")
    elif current == Form.company:
        await state.set_state(Form.phone)
        await message.answer("🔙 Вернулись. Введите номер телефона:")
    elif current == Form.tariff:
        await state.set_state(Form.company)
        await message.answer("🔙 Вернулись. Введите название компании:")
    else:
        await message.answer("⏪ Назад недоступен.")

# ФИО
@dp.message(Form.fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(Form.phone)
    await message.answer("📞 Введите номер телефона:")

# Телефон
@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Form.company)
    await message.answer("🏢 Введите название компании:")

# Компания
@dp.message(Form.company)
async def process_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(Form.tariff)
    await message.answer("📊 Выберите интересующий тариф:", reply_markup=tariff_keyboard)

# Тариф
@dp.message(Form.tariff)
async def process_tariff(message: Message, state: FSMContext):
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
    await message.answer("✅ Заявка отправлена! Наш менеджер скоро с вами свяжется.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# Запуск
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
