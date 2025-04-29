import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests

# Configuration
TELEGRAM_TOKEN = "7612286812:AAHvaGvI3BUmgTpSdI5fWWt_p7jtnb3O2Rw"
SENATOR_API_URL = "https://api.fast-creat.ir/photo-quality"
SENATOR_API_KEY = "7046488481:0Gpl8EFRJqZjywo@Api_ManagerRoBot"

# Set up logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos."""
    chat_id = update.message.chat_id
    logger.info(f"Received photo from chat {chat_id}")

    # Check for photo
    if not update.message.photo:
        await update.message.reply_text("Please send a photo!")
        logger.info(f"No photo in message from chat {chat_id}")
        return

    # Get highest resolution photo
    photo = update.message.photo[-1]
    try:
        # Get file URL
        file = await photo.get_file()
        photo_url = file.file_path
        logger.info(f"Photo URL: {photo_url}")

        # Call Senator API
        params = {"apikey": SENATOR_API_KEY, "url": photo_url}
        response = requests.get(SENATOR_API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Senator API response: {data}")

        # Check response
        if not data.get("ok") or data.get("status") != "successfully" or not data.get("result", {}).get("link"):
            logger.error(f"Invalid API response: {data}")
            await update.message.reply_text("Failed to enhance photo. Try again or contact @SenatorAPI.")
            return

        enhanced_url = data["result"]["link"]
        logger.info(f"Enhanced URL: {enhanced_url}")

        # Send enhanced photo
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=enhanced_url,
            caption="Enhanced photo!"
        )
        logger.info(f"Sent enhanced photo to chat {chat_id}")

    except requests.RequestException as e:
        logger.error(f"Senator API error: {str(e)}")
        await update.message.reply_text("Photo enhancement failed. Try again or contact @SenatorAPI.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text("An error occurred. Try again.")

def main() -> None:
    """Run the bot."""
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_TOKEN not set")
        raise ValueError("Set TELEGRAM_TOKEN in bot.py")

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start bot
    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
