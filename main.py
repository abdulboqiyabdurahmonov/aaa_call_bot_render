import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002344973979  # ID вашей Telegram-группы

# Этапы диалога
FULL_NAME, PHONE, COMPANY, TARIFF = range(4)

# Кнопки
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Оставить заявку"), KeyboardButton("Связаться с менеджером")]
    ],
    resize_keyboard=True
)

tariff_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["Старт", "Бизнес", "Корпоративный"],
        ["/назад", "/отменить"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать в TRIPLEA!\nНажмите «Оставить заявку», чтобы начать.",
        reply_markup=main_keyboard
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявка отменена.", reply_markup=main_keyboard)
    return ConversationHandler.END


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔙 Возвращаемся в главное меню.", reply_markup=main_keyboard)
    return ConversationHandler.END


async def start_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, введите ваше ФИО:")
    return FULL_NAME


async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("Теперь введите номер телефона:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите название вашей компании:")
    return COMPANY


async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    await update.message.reply_text(
        "Выберите интересующий тариф:",
        reply_markup=tariff_keyboard
    )
    return TARIFF


async def get_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tariff"] = update.message.text

    # Подготовим текст заявки
    full_name = context.user_data["full_name"]
    phone = context.user_data["phone"]
    company = context.user_data["company"]
    tariff = context.user_data["tariff"]

    message = (
        "📥 *Новая заявка:*\n\n"
        f"👤 *ФИО:* {full_name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"🏢 *Компания:* {company}\n"
        f"📦 *Тариф:* {tariff}"
    )

    await context.bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
    await update.message.reply_text("✅ Спасибо! Ваша заявка принята.", reply_markup=main_keyboard)

    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Оставить заявку"), start_form)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tariff)],
        },
        fallbacks=[
            CommandHandler("отменить", cancel),
            CommandHandler("назад", back),
        ]
    )

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("отменить", cancel))
    app.add_handler(CommandHandler("назад", back))
    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
