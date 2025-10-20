import os
import logging
from flask import Flask
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
import asyncio 

# This makes sure we can see what the bot is doing
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# IMPORTANT: Reads your secret token from Railway settings
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# --- 1. What the Bot Does ---
# This function runs when someone types /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The bot responds to the /start command."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hello, {user.mention_html()}! I am now running and ready for automation tasks."
    )

# --- 2. How the Bot Starts ---
def run_bot():
    """Sets up the bot application."""
    if not BOT_TOKEN:
        logger.error("ERROR: TELEGRAM_BOT_TOKEN is missing. Please set it in Railway.")
        return

    # Build the main Telegram application
    application = Application.builder().token(BOT_TOKEN).build()

    # Link the /start command to the 'start_command' function
    application.add_handler(CommandHandler("start", start_command))

    logger.info("Starting bot now...")
    
    # This command makes the bot continuously check for new messages
    asyncio.run(application.run_polling(poll_interval=1.0))


# --- 3. Railway Setup (Health Check) ---
# This is required because Railway (Gunicorn) needs a web application to start.
app = Flask(__name__)

@app.route("/")
def health_check():
    """Endpoint for Railway to check if the app is alive."""
    return "Telegram Bot is running!", 200

# When the program starts, it runs the bot
if __name__ == '__main__':
    run_bot()
