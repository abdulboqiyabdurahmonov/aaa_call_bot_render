from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import os

app = Flask(__name__)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dispatcher = Dispatcher(bot, None, use_context=True)

def start(update, context):
    update.message.reply_text("Привет! Я живой.")

dispatcher.add_handler(CommandHandler("start", start))

@app.route('/')
def home():
    return 'Бот жив'

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'
