import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне сообщение, и я передам его менеджеру.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.message.from_user
    text = update.message.text

    message = f"📩 Новое сообщение от @{user.username or user.first_name} (ID: {user.id}):\n{text}"
    if MANAGER_CHAT_ID:
        await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
    else:
        await update.message.reply_text("Ошибка: не задан MANAGER_CHAT_ID.")

    await update.message.reply_text("Спасибо, ваше сообщение отправлено менеджеру.")

if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("Не задан BOT_TOKEN в переменных среды")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()
    from telegram import ReplyKeyboardMarkup
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:",
        reply_markup=reply_markup
    )
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Оставить заявку":
        await update.message.reply_text("Пожалуйста, напишите ваше имя, телефон и email.")
    elif text == "Связаться с менеджером":
        manager_chat_id = os.getenv("MANAGER_CHAT_ID")
        await update.message.reply_text(f"Менеджер свяжется с вами. Или напишите напрямую: @{manager_chat_id}")
    else:
        await update.message.reply_text("Я получил твоё сообщение! Скоро с тобой свяжется менеджер.")



