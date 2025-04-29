import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
import tempfile

# Bot configuration
API_ID = "15787995"  # Replace with your Telegram API ID
API_HASH = "e51a3154d2e0c45e5ed70251d68382de"  # Replace with your Telegram API Hash
BOT_TOKEN = "7612286812:AAHvaGvI3BUmgTpSdI5fWWt_p7jtnb3O2Rw"  # Replace with your Telegram Bot Token
ENHANCE_API_URL = "https://api.fast-creat.ir/photo-quality"
API_KEY = "7046488481:0Gpl8EFRJqZjywo@Api_ManagerRoBot"
CATBOX_UPLOAD_URL = "https://catbox.moe/user/api.php"

# Initialize Pyrogram client
app = Client("PhotoEnhanceBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Helper function to upload photo to catbox.moe
async def upload_to_catbox(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {"fileToUpload": f}
            data = {"reqtype": "fileupload"}
            response = requests.post(CATBOX_UPLOAD_URL, data=data, files=files)
            if response.status_code == 200 and response.text.startswith("https://"):
                return response.text.strip()
            else:
                return None
    except Exception as e:
        print(f"Upload error: {e}")
        return None

# Helper function to call the photo enhancement API
def enhance_photo(photo_url):
    try:
        params = {"apikey": API_KEY, "url": photo_url}
        response = requests.get(ENHANCE_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("status") == "successfully":
                return data["result"]["link"]
        return None
    except Exception as e:
        print(f"API error: {e}")
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

        # Download the photo
        photo = message.photo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            file_path = temp_file.name
            await photo.download(file_path)

        # Upload photo to catbox.moe to get a public URL
        photo_url = await upload_to_catbox(file_path)
        if not photo_url:
            await status_msg.edit_text("Failed to upload the photo. Please try again.")
            os.remove(file_path)
            return

        # Call the enhancement API
        enhanced_url = enhance_photo(photo_url)
        if not enhanced_url:
            await status_msg.edit_text("Failed to enhance the photo. The API may be down or the photo is invalid.")
            os.remove(file_path)
            return

        # Send the enhanced photo URL to the user
        await status_msg.edit_text(f"Here’s your enhanced photo:\n{enhanced_url}")

        # Clean up the temporary file
        os.remove(file_path)

    except Exception as e:
        await status_msg.edit_text("An error occurred. Please try again later.")
        print(f"Error: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
