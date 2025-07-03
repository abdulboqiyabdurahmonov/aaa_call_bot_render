import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Загружаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:",
        reply_markup=reply_markup
    )

# Обработка кнопок и сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text
    user = update.message.from_user

    if text == "Оставить заявку":
        await update.message.reply_text("Пожалуйста, напишите ваше имя, телефон и email.")
    elif text == "Связаться с менеджером":
        if MANAGER_CHAT_ID:
            await update.message.reply_text(f"Наш менеджер свяжется с вами в ближайшее время.\n"
                                            f"Вы также можете написать ему напрямую: @{MANAGER_CHAT_ID}")
        else:
            await update.message.reply_text("Ошибка: не задан MANAGER_CHAT_ID.")
    else:
        # Отправка заявки менеджеру
        message = f"📩 Новое сообщение от @{user.username or user.first_name} (ID: {user.id}):\n{text}"
        if MANAGER_CHAT_ID:
            await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
        await update.message.reply_text("Спасибо, ваше сообщение отправлено менеджеру.")

# Запуск бота
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError("Не задан BOT_TOKEN в переменных среды")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен...")
    app.run_polling()
    from telegram import ReplyKeyboardMarkup

reply_markup = ReplyKeyboardMarkup(
    [['📝 Оставить заявку', '📞 Связаться с менеджером']],
    resize_keyboard=True
)
update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

