import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Загружаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Этапы разговора
(ASK_NAME, ASK_PHONE, ASK_COMPANY, ASK_TARIFF) = range(4)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Привет! 👋\nПожалуйста, укажите ваше полное имя:")
    return ASK_NAME

# Получение имени
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Спасибо! Теперь введите номер телефона:")
    return ASK_PHONE

# Получение телефона
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Отлично! Введите название вашей компании:")
    return ASK_COMPANY

# Получение компании
async def ask_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["company"] = update.message.text

    keyboard = [["Старт", "Бизнес", "Корпоративный"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Какой тариф вас интересует?", reply_markup=reply_markup)
    return ASK_TARIFF

# Получение тарифа и отправка менеджеру
async def ask_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["tariff"] = update.message.text

    user_data = context.user_data
    message = (
        "📩 Новая заявка:\n"
        f"👤 Имя: {user_data['name']}\n"
        f"📞 Телефон: {user_data['phone']}\n"
        f"🏢 Компания: {user_data['company']}\n"
        f"💼 Тариф: {user_data['tariff']}"
    )

    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
    await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру ✅", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Обработка отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company)],
            ASK_TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_tariff)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


 
