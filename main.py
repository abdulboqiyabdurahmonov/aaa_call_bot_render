import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters,
    ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # сюда укажешь ID группы или лички

# Состояния для разговора
FIO, PHONE, COMPANY, TARIFF = range(4)

# Главное меню
main_keyboard = ReplyKeyboardMarkup(
    [["Оставить заявку", "Связаться с менеджером"]],
    resize_keyboard=True
)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот TRIPLEA.\n\n"
        "Я помогу тебе оставить заявку или связаться с менеджером.",
        reply_markup=main_keyboard
    )

# Help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — начать\n"
        "/help — помощь\n"
        "/cancel — отмена\n"
        "/chatid — узнать ID чата"
    )

# /chatid — узнать ID
async def chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🔍 Chat ID: `{chat_id}`", parse_mode="Markdown")

# Начинаем сбор заявки
async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, введи своё ФИО:")
    return FIO

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text("Теперь номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Как называется ваша компания?")
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    await update.message.reply_text(
        "Выберите интересующий тариф: старт, бизнес или корпоративный"
    )
    return TARIFF

async def get_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tariff"] = update.message.text

    text = (
        "📥 Новая заявка\n\n"
        f"👤 ФИО: {context.user_data['fio']}\n"
        f"📞 Телефон: {context.user_data['phone']}\n"
        f"🏢 Компания: {context.user_data['company']}\n"
        f"💼 Тариф: {context.user_data['tariff']}"
    )

    await update.message.reply_text("Спасибо! Ваша заявка отправлена менеджеру.")

    # Отправка админу
    if ADMIN_CHAT_ID:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    else:
        await update.message.reply_text("❗ ADMIN_CHAT_ID не указан.")

    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Заявка отменена.", reply_markup=main_keyboard)
    return ConversationHandler.END

# Меню
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "заявку" in text:
        return await start_application(update, context)
    elif "менеджером" in text:
        await update.message.reply_text("Скоро с вами свяжется наш менеджер 👨‍💼")
    else:
        await update.message.reply_text("Выберите действие в меню ⬇")

# Сборка
app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^(Оставить заявку)$"), start_application)],
    states={
        FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
        TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tariff)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("chatid", chat_id_command))
app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("✅ Бот запущен...")
app.run_polling()

