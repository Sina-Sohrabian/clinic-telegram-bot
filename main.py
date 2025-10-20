import os
import logging
from flask import Flask, request, jsonify
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
import asyncio 

# This makes sure we can see what the bot is doing
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# IMPORTANT: Reads your secret token and environment URL
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Cloud providers like Railway often expose the service URL via an environment variable
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") 
PORT = int(os.environ.get("PORT", 5000))

# --- 1. What the Bot Does ---
# This function runs when someone types /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """The bot responds to the /start command."""
    user = update.effective_user
    logger.info(f"Received /start from user {user.id}")
    await update.message.reply_html(
        f"Hello, {user.mention_html()}! I am now running via Webhooks and ready for automation tasks."
    )

# --- 2. How the Bot is Configured (Application Instance) ---
# We instantiate the application globally so the Flask routes can access it later
if BOT_TOKEN:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    logger.info("Telegram Application built successfully.")
else:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN is missing. Application cannot be built.")
    application = None


# --- 3. Flask Webhook Setup ---

# This is required because the server needs a web application to start.
app = Flask(__name__)

@app.route("/")
def health_check():
    """Endpoint for the server to check if the app is alive."""
    if not BOT_TOKEN:
        return "ERROR: Bot token is missing.", 500
    return "Telegram Bot Webhook Receiver is ready!", 200

# This is the dedicated endpoint that Telegram will send messages to
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook_handler():
    """Handle incoming Telegram updates (messages)."""
    if application is None:
        logger.error("Application is not initialized. Cannot process updates.")
        return jsonify({}), 500

    # Ensure the request came from Telegram's servers and is JSON
    if request.json:
        # Convert the JSON body into a Telegram Update object and process it
        update = Update.de_json(request.json, application.bot)
        
        # Process the update asynchronously
        await application.process_update(update)

        return jsonify({}), 200
    
    return "Bad Request", 400

# --- 4. Function to Set Webhook on Startup ---
# This is crucial: we must tell Telegram where to send updates.
async def set_webhook():
    if application and WEBHOOK_URL:
        # Construct the full URL where the bot should receive updates
        webhook_path = f"/{BOT_TOKEN}"
        full_webhook_url = WEBHOOK_URL + webhook_path
        
        # Check if the webhook is already set correctly
        current_webhook = await application.bot.get_webhook_info()
        if current_webhook.url != full_webhook_url:
            # Set the webhook to point to our Flask endpoint
            await application.bot.set_webhook(url=full_webhook_url)
            logger.info(f"Webhook set successfully to: {full_webhook_url}")
        else:
            logger.info("Webhook already correctly set.")
    elif not WEBHOOK_URL:
         logger.warning("WEBHOOK_URL is missing. Could not set webhook. Bot will only work if manually set.")


# --- 5. Main Execution ---
if __name__ == '__main__':
    # Start the webhook configuration task
    asyncio.run(set_webhook())
    
    # Run the Flask web server
    logger.info(f"Starting Flask server on port {PORT}...")
    # NOTE: You must use 'gunicorn main:app' command for production environments
    # For local testing, you can uncomment app.run()
    # app.run(host='0.0.0.0', port=PORT, debug=True)
    
# NOTE FOR DEPLOYMENT:
# In your production environment (like Railway), you should use a command 
# like 'gunicorn main:app' to start the web server, which will automatically 
# execute the global setup code and allow Flask to handle the webhooks.
