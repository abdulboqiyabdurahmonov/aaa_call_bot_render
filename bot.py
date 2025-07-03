import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот TRIPLEA. Я могу принимать заявки и помогать с обратной связью.\n\n"
        "Напиши /help, чтобы узнать, что я умею."
    )


# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вот что я умею:\n"
        "/start – Начать работу\n"
        "/help – Показать это сообщение\n"
        "Просто напиши мне, и я подскажу, что делать дальше!"
    )


# Ответ на обычный текст
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я получил твоё сообщение! Скоро с тобой свяжется менеджер.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Хэндлеры команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Хэндлер текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()

