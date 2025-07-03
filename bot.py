import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Переменные окружения
BOT_TOKEN = "7993696802:AAHsaOyLkComr4mr2WsC-EgnB5jcHKjd7Ho"
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Состояния
(ASK_NAME, ASK_PHONE, ASK_COMPANY, ASK_TARIFF) = range(4)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:", reply_markup=reply_markup
    )

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Назад
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END

# Выбор действия
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Оставить заявку":
        await update.message.reply_text("Пожалуйста, введите ваше ФИО:", reply_markup=ReplyKeyboardRemove())
        return ASK_NAME
    elif choice == "Связаться с менеджером":
        await update.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выберите один из доступных вариантов.")
        return ConversationHandler.END

# Сбор информации
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return ASK_PHONE

async def ask_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите название компании:")
    return ASK_COMPANY

async def ask_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    await update.message.reply_text(
        "💼 Тарифы: \n"
        "1. Старт — до 1 000 звонков, 1 сценарий, поддержка Telegram, быстрый запуск — 900 000 сум/мес\n"
        "2. Бизнес — до 10 000 звонков, 5 сценариев, аналитика, Telegram-бот — 8 100 000 сум/мес\n"
        "3. Корпоративный — до 100 000 звонков, неограниченные сценарии, API и менеджер — 72 900 000 сум/мес\n"
        "\nВведите название тарифа:"
    )
    return ASK_TARIFF

# Завершение
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tariff"] = update.message.text
    user_data = context.user_data

    message = (
        f"📥 Новая заявка:\n"
        f"👤 ФИО: {user_data['name']}\n"
        f"📞 Телефон: {user_data['phone']}\n"
        f"🏢 Компания: {user_data['company']}\n"
        f"💼 Тариф: {user_data['tariff']}"
    )

    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
    await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

# Основной
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), handle_choice)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company)],
            ASK_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_tariff)],
            ASK_TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("назад", go_back),
            CommandHandler("отменить", cancel),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("назад", go_back))
    app.add_handler(CommandHandler("отменить", cancel))

    app.run_polling()

