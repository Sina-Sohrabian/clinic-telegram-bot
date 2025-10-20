from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

# Create a small web server for Railway
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

# Telegram Bot Token (replace with your real one)
TOKEN = os.getenv("BOT_TOKEN")

# Define a simple start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I’m your clinic assistant bot 🤖")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
