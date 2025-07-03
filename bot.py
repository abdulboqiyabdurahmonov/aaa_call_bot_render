import os
from telegram import Update
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
        "🆘 *Команды бота:*\n"
        "/start — начать диалог\n"
        "/help — справка по использованию\n"
        "Просто напиши данные — и бот примет заявку ✉️",
        parse_mode="Markdown"
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
        manager_chat_id = os.getenv(\"MANAGER_CHAT_ID\")
    message = f\"📥 Новая заявка\\n\\n👤 Имя: {context.user_data['name']}\\n📞 Телефон: {context.user_data['phone']}\"

    try:
        await context.bot.send_message(chat_id=manager_chat_id, text=message)
    except Exception as e:
        print(\"Ошибка при отправке менеджеру:\", e)



if __name__ == "__main__":
    main()
