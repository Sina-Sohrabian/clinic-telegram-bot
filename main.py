from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

# Flask app to keep Railway alive
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running on Railway!"

# Telegram bot setup
TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! 👋 I’m your clinic assistant bot — ready to help you!")

def run_bot():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    # Run both bot and Flask server at the same time
    Thread(target=run_bot).start()
    run_flask()
