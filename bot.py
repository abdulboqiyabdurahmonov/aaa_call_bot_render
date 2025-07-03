import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)

TOKEN = "7993696802:AAHsaOyLkComr4mr2WsC-EgnB5jcHKjd7Ho"
GROUP_ID = -100xxxxxxxxxxxx  # <-- сюда вставь ID своей Telegram-группы

logging.basicConfig(level=logging.INFO)

(
    GET_NAME,
    GET_PHONE,
    GET_COMPANY,
    GET_TARIFF
) = range(4)

tariff_info = {
    "Старт": "Для малого бизнеса и тестов\n• До 1 000 звонков в месяц\n• 1 голосовой сценарий\n• Поддержка в Telegram\n• Быстрый запуск\n💰 900 000 сум / мес",
    "Бизнес": "Для растущих отделов продаж\n• До 10 000 звонков в месяц\n• До 5 сценариев\n• Поддержка и аналитика\n• Интеграция с Telegram-ботом\n💰 8 100 000 сум / мес",
    "Корпоративный": "Для крупных проектов и сетей\n• До 100 000 звонков в месяц\n• Неограниченные сценарии\n• API-интеграция, CRM\n• Персональный менеджер\n💰 72 900 000 сум / мес"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Оставить заявку", callback_data="leave_request")],
        [InlineKeyboardButton("Связаться с менеджером", callback_data="contact_manager")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "leave_request":
        await query.message.reply_text("Пожалуйста, напишите ваше ФИО:")
        return GET_NAME
    elif query.data == "contact_manager":
        await query.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Теперь введите номер телефона:")
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите название вашей компании:")
    return GET_COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Старт", callback_data="Старт")],
        [InlineKeyboardButton("Бизнес", callback_data="Бизнес")],
        [InlineKeyboardButton("Корпоративный", callback_data="Корпоративный")]
    ]
    await update.message.reply_text("Выберите интересующий тариф:", reply_markup=InlineKeyboardMarkup(keyboard))
    return GET_TARIFF

async def get_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tariff = query.data
    context.user_data["tariff"] = tariff
    message = (
        "📥 Новая заявка\n\n"
        f"👤 ФИО: {context.user_data['name']}\n"
        f"📞 Телефон: {context.user_data['phone']}\n"
        f"🏢 Компания: {context.user_data['company']}\n"
        f"📦 Тариф: {tariff}\n\n"
        f"ℹ️ Подробнее о тарифе:\n{tariff_info[tariff]}"
    )
    await context.bot.send_message(chat_id=GROUP_ID, text=message)
    await query.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено. Введите /start для начала.")
    return ConversationHandler.END

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы вернулись назад. Введите /start.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            GET_TARIFF: [CallbackQueryHandler(get_tariff)]
        },
        fallbacks=[
            CommandHandler("отменить", cancel),
            CommandHandler("назад", go_back)
        ]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    # Webhook для Render (используй свой домен если есть)
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url="https://<твоя-ссылка>.onrender.com"
    )

if __name__ == "__main__":
    main()
