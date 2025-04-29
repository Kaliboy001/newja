import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto

# Bot configuration
API_ID = "15787995"  # Replace with your Telegram API ID
API_HASH = "e51a3154d2e0c45e5ed70251d68382de"  # Replace with your Telegram API Hash
BOT_TOKEN = "7612286812:AAHvaGvI3BUmgTpSdI5fWWt_p7jtnb3O2Rw"  # Replace with your Bot Token
ENHANCE_API_KEY = "7046488481:0Gpl8EFRJqZjywo@Api_ManagerRoBot"

app = Client("photo_enhancer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def enhance_photo(photo_url):
    api_url = f"https://api.fast-creat.ir/photo-quality?apikey={ENHANCE_API_KEY}&url={photo_url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("ok") and data.get("status") == "successfully":
                    return data["result"]["link"]
            return None

@app.on_message(filters.command(["start"]))
async def start(client, message):
    await message.reply_text("Send me a photo, and I'll enhance it for you!")

@app.on_message(filters.photo)
async def handle_photo(client, message):
    try:
        # Get the photo file
        photo = message.photo
        file_id = photo.file_id
        
        # Get the file path from Telegram
        file = await client.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        
        # Send processing message
        processing_msg = await message.reply_text("Enhancing your photo... Please wait.")
        
        # Enhance the photo using the API
        enhanced_url = await enhance_photo(file_url)
        
        if enhanced_url:
            # Send the enhanced photo
            await message.reply_media_group([InputMediaPhoto(enhanced_url)])
            await processing_msg.edit_text("Photo enhanced successfully!")
        else:
            await processing_msg.edit_text("Failed to enhance the photo. Please try again.")
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run()
