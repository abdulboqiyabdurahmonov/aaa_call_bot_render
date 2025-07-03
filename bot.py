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

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Этапы диалога
NAME, PHONE, COMPANY, TARIFF = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:",
        reply_markup=reply_markup
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Оставить заявку":
        await update.message.reply_text("Пожалуйста, укажите ваше ФИО:")
        return NAME
    elif text == "Связаться с менеджером":
        await update.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.")
        return ConversationHandler.END

async def collect_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Укажите ваш номер телефона:")
    return PHONE

async def collect_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите название вашей компании:")
    return COMPANY

async def collect_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    await update.message.reply_text(
        "📦 Тарифы: \n"
        "1️⃣ Старт — 900 000 сум/мес\n"
        "   До 1 000 звонков, 1 сценарий, Telegram-поддержка\n\n"
        "2️⃣ Бизнес — 8 100 000 сум/мес\n"
        "   До 10 000 звонков, 5 сценариев, аналитика, Telegram-бот\n\n"
        "3️⃣ Корпоративный — 72 900 000 сум/мес\n"
        "   До 100 000 звонков, API, CRM, персональный менеджер\n\n"
        "Какой тариф вас интересует?"
    )
    return TARIFF

async def collect_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tariff"] = update.message.text

    message = (
        "📥 Новая заявка:\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"📞 Телефон: {context.user_data['phone']}\n"
        f"🏢 Компания: {context.user_data['company']}\n"
        f"💼 Тариф: {context.user_data['tariff']}"
    )

    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=message)
    await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), handle_choice)],
        states={
            NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), collect_name)],
            PHONE: [MessageHandler(filters.TEXT & (~filters.COMMAND), collect_phone)],
            COMPANY: [MessageHandler(filters.TEXT & (~filters.COMMAND), collect_company)],
            TARIFF: [MessageHandler(filters.TEXT & (~filters.COMMAND), collect_tariff)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("back", back),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.run_polling()
