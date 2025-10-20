# main.py
import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# Get token from environment (we'll set this on Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Create dispatcher for handling updates (no persistence)
dispatcher = Dispatcher(bot, None, workers=4)

# --- Handlers ---
def start(update, context):
    chat_id = update.effective_chat.id
    bot.send_message(chat_id=chat_id, text="Hello! Clinic bot is online. How can I help?")

def echo(update, context):
    text = update.message.text or ""
    bot.send_message(chat_id=update.effective_chat.id, text="You said: " + text)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Webhook endpoint Telegram will POST to ---
@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, bot)
    dispatcher.process_update(update)
    return "OK", 200

# --- Local/run configuration (Railway sets PORT env var) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
