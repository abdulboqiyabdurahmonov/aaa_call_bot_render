import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Загружаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Этапы собрания данных
FIO, PHONE, COMPANY, TARIFF = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привет!\nВыберите, что хотите сделать:",
        reply_markup=reply_markup
    )

async def contact_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\u041d\u0430\u0448 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0441\u0432\u044f\u0436\u0435\u0442\u0441\u044f \u0441 \u0432\u0430\u043c\u0438 \u0432 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u0432\u0440\u0435\u043c\u044f.")

async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Пожалуйста, напишите своё ФИО:")
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['fio'] = update.message.text
    await update.message.reply_text("📱 Теперь ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("🏢 Ваша компания:")
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company'] = update.message.text
    await update.message.reply_text("📈 Тариф: \n1. Старт \n2. Бизнес \n3. Корпоративный\n
💬 Выберите один из тарифов:")
    return TARIFF

async def get_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tariff'] = update.message.text
    text = (
        f"📢 Новая заявка:\n"
        f"👤 ФИО: {context.user_data['fio']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n"
        f"🏢 Компания: {context.user_data['company']}\n"
        f"📈 Тариф: {context.user_data['tariff']}"
    )
    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=text)
    await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^\О\с\т\а\в\и\т\ь \з\а\я\в\к\у$"), start_application)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tariff)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("отменить", cancel), CommandHandler("назад", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("отменить", cancel))
    app.add_handler(CommandHandler("назад", start))
    app.add_handler(MessageHandler(filters.Regex("^\С\в\я\з\а\т\ь\с\я \с \м\е\н\е\д\ж\е\р\о\м$"), contact_manager))
    app.add_handler(conv_handler)

    app.run_polling()
