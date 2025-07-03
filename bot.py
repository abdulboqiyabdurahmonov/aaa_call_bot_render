
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = os.getenv("7993696802:AAHsaOyLkComr4mr2WsC-EgnB5jcHKjd7Ho")
OWNER_ID = os.getenv("349680069")
MANAGER_CHAT_ID = os.getenv("557891018")
PORT = int(os.environ.get("PORT", 10000))
HOSTNAME = os.getenv("aaa_call_bot_rende")

TYPING_NAME, TYPING_PHONE, TYPING_COMPANY, CHOOSING_PLAN = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Оставить заявку", "Связаться с менеджером"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\nВыберите, что хотите сделать:",
        reply_markup=reply_markup
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Связаться с менеджером":
        await update.message.reply_text("Наш менеджер свяжется с вами в ближайшее время.")
        return ConversationHandler.END
    elif text == "Оставить заявку":
        await update.message.reply_text("Пожалуйста, напишите ваше ФИО:")
        return TYPING_NAME
    else:
        await update.message.reply_text("Пожалуйста, выберите действие с помощью кнопок.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено. Введите /start, чтобы начать заново.")
    return ConversationHandler.END

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите номер телефона:")
    return TYPING_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите название вашей компании:")
    return TYPING_COMPANY

async def handle_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["company"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([["Старт", "Бизнес", "Корпоративный"]], resize_keyboard=True)
    await update.message.reply_text("Выберите интересующий тариф:", reply_markup=reply_markup)
    return CHOOSING_PLAN

async def handle_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = update.message.text
    context.user_data["plan"] = plan
    data = context.user_data

    tariff_info = {
        "Старт": "До 1 000 звонков в месяц\n1 голосовой сценарий\nПоддержка в Telegram\nБыстрый запуск\n900 000 сум / мес",
        "Бизнес": "До 10 000 звонков в месяц\nДо 5 сценариев\nПоддержка и аналитика\nИнтеграция с Telegram-ботом\n8 100 000 сум / мес",
        "Корпоративный": "До 100 000 звонков в месяц\nНеограниченные сценарии\nAPI-интеграция, CRM\nПерсональный менеджер\n72 900 000 сум / мес"
    }

    msg = f"\U0001F4E5 Новая заявка:\n\U0001F464 ФИО: {data['name']}\n\U0001F4DE Телефон: {data['phone']}\n\U0001F3E2 Компания: {data['company']}\n\U0001F4E6 Тариф: {plan}\n\U0001F4C4 Подробности: {tariff_info.get(plan, 'Неизвестный тариф')}"
    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=msg)
    await update.message.reply_text("Спасибо, ваша заявка отправлена менеджеру.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)],
        states={
            TYPING_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_name)],
            TYPING_PHONE: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_phone)],
            TYPING_COMPANY: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_company)],
            CHOOSING_PLAN: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_plan)],
        },
        fallbacks=[
            CommandHandler("отменить", cancel),
            CommandHandler("назад", back),
            CommandHandler("start", start)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{HOSTNAME}/"
    )

if __name__ == "__main__":
    main()

