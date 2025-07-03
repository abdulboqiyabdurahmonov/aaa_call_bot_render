from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Константы этапов диалога
NAME, PHONE, COMPANY, TARIFF = range(4)

# ID вашей группы
GROUP_ID = -1002344973979

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Оставить заявку', 'Связаться с менеджером']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Привет! 👋\nВыберите, что хотите сделать:", reply_markup=reply_markup)

# Логика нажатий кнопок
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == 'Оставить заявку':
        await update.message.reply_text("Пожалуйста, введите ваше ФИО:")
        return NAME
    elif text == 'Связаться с менеджером':
        await update.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Пожалуйста, выберите один из пунктов меню.")
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Введите название вашей компании:")
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company'] = update.message.text
    await update.message.reply_text("Выберите интересующий тариф:\n1. Старт\n2. Бизнес\n3. Корпоративный")
    return TARIFF

async def get_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tariff'] = update.message.text

    tariff_description = {
        "Старт": "До 1 000 звонков в месяц\n1 голосовой сценарий\nПоддержка в Telegram\nБыстрый запуск\n💵 900 000 сум / мес",
        "Бизнес": "До 10 000 звонков в месяц\nДо 5 сценариев\nПоддержка и аналитика\nИнтеграция с Telegram-ботом\n💵 8 100 000 сум / мес",
        "Корпоративный": "До 100 000 звонков в месяц\nНеограниченные сценарии\nAPI-интеграция, CRM\nПерсональный менеджер\n💵 72 900 000 сум / мес"
    }

    name = context.user_data.get("name")
    phone = context.user_data.get("phone")
    company = context.user_data.get("company")
    tariff = context.user_data.get("tariff")

    message = (
        f"📥 Новая заявка\n\n"
        f"👤 ФИО: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"🏢 Компания: {company}\n"
        f"📦 Тариф: {tariff}\n\n"
        f"ℹ️ Подробнее о тарифе:\n{tariff_description.get(tariff, 'Информация не найдена')}"
    )

    await context.bot.send_message(chat_id=GROUP_ID, text=message)
    await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

# Команда отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.")
    return ConversationHandler.END

# Команда назад
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы вернулись назад.")
    return ConversationHandler.END

# Запуск приложения
app = ApplicationBuilder().token("7993696802:AAHsaOyLkComr4mr2WsC-EgnB5jcHKjd7Ho").build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
        TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tariff)],
    },
    fallbacks=[CommandHandler("cancel", cancel), CommandHandler("back", back)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("back", back))
app.add_handler(conv_handler)

# Запуск через Webhook
app.run_webhook(
    listen="0.0.0.0",
    port=8080,
    webhook_url="https://aaa-call-bot.onrender.com"  # Убедись, что эта ссылка активна!
)
