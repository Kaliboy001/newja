import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = 15787995
API_HASH = "e51a3154d2e0c45e5ed70251d68382de"
BOT_TOKEN = "7612286812:AAHvaGvI3BUmgTpSdI5fWWt_p7jtnb3O2Rw"
ENHANCE_API_URL = "https://api.fast-creat.ir/photo-quality"
API_KEY = "7046488481:0Gpl8EFRJqZjywo@Api_ManagerRoBot"

# Initialize Pyrogram client
app = Client("PhotoEnhanceBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Helper function to get Telegram file URL
async def get_telegram_file_url(client: Client, file_id: str) -> str:
    try:
        file = await client.get_file(file_id)
        file_path = file.file_path
        # Telegram file URLs are temporary and accessible via the bot
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        logger.info(f"Generated Telegram file URL: {file_url}")
        return file_url
    except Exception as e:
        logger.error(f"Failed to get Telegram file URL: {e}")
        return None

# Helper function to call the photo enhancement API
def enhance_photo(photo_url: str) -> str:
    try:
        params = {"apikey": API_KEY, "url": photo_url}
        logger.info(f"Sending API request with URL: {photo_url}")
        response = requests.get(ENHANCE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"API response: {data}")
        if data.get("ok") and data.get("status") == "successfully" and data.get("result", {}).get("link"):
            return data["result"]["link"]
        logger.error(f"API response invalid: {data}")
        return None
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return None

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "Hello! I'm a Photo Enhancer Bot. Send me a photo, and I'll enhance it using an AI-powered API. "
        "You'll receive a URL to the enhanced photo. Try it now!"
    )

# Photo message handler
@app.on_message(filters.photo)
async def handle_photo(client: Client, message: Message):
    try:
        # Send a processing message
        status_msg = await message.reply_text("Processing your photo...")

        # Get the photo file ID
        photo = message.photo
        file_id = photo.file_id

        # Get the Telegram file URL
        photo_url = await get_telegram_file_url(client, file_id)
        if not photo_url:
            await status_msg.edit_text("Failed to access the photo. Please try again.")
            return

        # Call the enhancement API
        enhanced_url = enhance_photo(photo_url)
        if not enhanced_url:
            await status_msg.edit_text(
                "Failed to enhance the photo. The API may be down or the photo is invalid. Please try again."
            )
            return

        # Send the enhanced photo URL to the user
        await status_msg.edit_text(f"Here’s your enhanced photo:\n{enhanced_url}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.reply_text("An error occurred. Please try again later.")

# Run the bot
if __name__ == "__main__":
    logger.info("Starting PhotoEnhanceBot...")
    app.run()
