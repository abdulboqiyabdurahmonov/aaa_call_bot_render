
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import os

# === НАСТРОЙКИ ===
TOKEN = "7993696802:AAHsaOyLkComr4mr2WsC-EgnB5jcHKjd7Ho"
WEBHOOK_URL = "https://aaa-call-bot-render.onrender.com/webhook"

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === СЛУЖЕБНЫЕ ПЕРЕМЕННЫЕ ===
user_data = {}

# === КОМАНДА /START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Оставить заявку", callback_data="request"),
            InlineKeyboardButton("Связаться с менеджером", callback_data="contact"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! 👋\nВыберите, что хотите сделать:", reply_markup=reply_markup)

# === КНОПКИ ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "request":
        user_data[query.from_user.id] = {}
        await query.message.reply_text("Пожалуйста, введите ваше ФИО:")
        context.user_data["step"] = "fio"

    elif query.data == "contact":
        await query.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")

# === СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЯ ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    uid = update.message.from_user.id
    text = update.message.text

    if step == "fio":
        user_data[uid]["fio"] = text
        context.user_data["step"] = "phone"
        await update.message.reply_text("Введите номер телефона:")

    elif step == "phone":
        user_data[uid]["phone"] = text
        context.user_data["step"] = "company"
        await update.message.reply_text("Введите название компании:")

    elif step == "company":
        user_data[uid]["company"] = text
        context.user_data["step"] = "tariff"
        await update.message.reply_text("Выберите тариф (Старт, Бизнес, Корпоративный):")

    elif step == "tariff":
        user_data[uid]["tariff"] = text
        context.user_data["step"] = None

        msg = (
            "📥 Новая заявка\n\n"
            f"👤 ФИО: {user_data[uid]['fio']}\n"
            f"📞 Телефон: {user_data[uid]['phone']}\n"
            f"🏢 Компания: {user_data[uid]['company']}\n"
            f"📦 Тариф: {user_data[uid]['tariff']}"
        )

        MANAGER_ID = 557891018  # Подставь нужный ID
        await context.bot.send_message(chat_id=MANAGER_ID, text=msg)
        await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")

    else:
        await update.message.reply_text("Пожалуйста, выберите действие через /start.")

# === ОСНОВНОЙ ФУНКЦИОНАЛ ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
    git add bot.py
git commit -m "Switch to webhook version"
git push


