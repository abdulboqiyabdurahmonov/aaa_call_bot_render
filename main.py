import logging
import os
import re
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Шаги
NAME, PHONE, EMAIL, LANGUAGE, COMMENT = range(5)

# Авторизация Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("TRIPLEA Заявки").sheet1

# Telegram ID владельца
OWNER_ID = int(os.getenv("OWNER_ID"))

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Как тебя зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Укажи номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not re.match(r"^\+?\d{9,15}$", phone):
        await update.message.reply_text("Некорректный номер. Попробуй ещё раз:")
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("Email (необязательно):")
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("На каком языке общаться? (Русский/Узбекский):")
    return LANGUAGE

async def get_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["language"] = update.message.text
    await update.message.reply_text("Оставь комментарий или нажми Enter для пропуска:")
    return COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text
    data = context.user_data
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Отправка в таблицу
    sheet.append_row([
        date,
        data["name"],
        data["phone"],
        data["email"],
        data["language"],
        data["comment"]
    ])

    # Отправка владельцу
    text = f"Новая заявка:\nИмя: {data['name']}\nТелефон: {data['phone']}\nEmail: {data['email']}\nЯзык: {data['language']}\nКомментарий: {data['comment']}"
    await context.bot.send_message(chat_id=OWNER_ID, text=text)

    await update.message.reply_text("Спасибо! Мы с вами свяжемся.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_language)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я получил твоё сообщение.")

def main():
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == "__main__":
    main()
    from fastapi import FastAPI, Request
import uvicorn
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

app = FastAPI()
bot = ApplicationBuilder().token(BOT_TOKEN).build()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot.bot)
    await bot.process_update(update)
    return {"status": "ok"}


    )

    app.add_handler(conv_handler)
    app.run_polling()
