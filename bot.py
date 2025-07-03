
import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# Загрузка переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Состояния
ASK_NAME, ASK_PHONE, ASK_COMPANY, ASK_TARIFF = range(4)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:", reply_markup=reply_markup
    )

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Оставить заявку":
        await update.message.reply_text("Пожалуйста, напишите ваше ФИО:")
        return ASK_NAME

    elif text == "Связаться с менеджером":
        await update.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")
        return ConversationHandler.END

    else:
        await update.message.reply_text("Пожалуйста, выберите действие с помощью кнопок.")
        return ConversationHandler.END

# Сбор информации
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Спасибо! Теперь введите ваш номер телефона:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Укажите название вашей компании:")
    return ASK_COMPANY

async def ask_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    await update.message.reply_text(
        "📑 Тарифы:
"
        "1. Старт — До 1 000 звонков в месяц, 1 сценарий, поддержка в Telegram, быстрый запуск.
"
        "2. Бизнес — До 10 000 звонков, 5 сценариев, аналитика, интеграция с ботом.
"
        "3. Корпоративный — До 100 000 звонков, неограниченные сценарии, API/CRM, персональный менеджер.
"
        "Введите интересующий тариф (Старт / Бизнес / Корпоративный):"
    )
    return ASK_TARIFF

async def ask_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tariff"] = update.message.text
    user = update.effective_user

    message = (
        f"📥 Новая заявка от @{user.username or 'Без ника'} (ID: {user.id}):\n"
        f"👤 ФИО: {context.user_data['name']}\n"
        f"📞 Телефон: {context.user_data['phone']}\n"
        f"🏢 Компания: {context.user_data['company']}\n"
        f"📦 Тариф: {context.user_data['tariff']}"
    )

    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
    await update.message.reply_text("Спасибо, ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

# Отмена и назад
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

# Главная функция
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company)],
            ASK_TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_tariff)],
        },
        fallbacks=[CommandHandler("отменить", cancel), CommandHandler("назад", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("назад", start))
    app.add_handler(CommandHandler("отменить", cancel))

    app.run_polling()

if __name__ == "__main__":
    main()
