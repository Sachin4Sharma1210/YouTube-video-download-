import os
import asyncio
import time
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
from flask import Flask
from threading import Thread

# --- Flask Server ---
web_app = Flask(__name__)
@web_app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- कॉन्फ़िगरेशन ---
API_ID = 29218807
API_HASH = "5de693a39423272c34457419323466a1"
BOT_TOKEN = "8441306868:AAFiY_FTmyljnldJq6da8NcESkH5hVXCiLA"
UPDATE_CHANNEL = "Sachin4Sharma1210"

# यहाँ 'in_memory=True' बहुत ज़रूरी है Render के लिए
app = Client(
    "yt_downloader",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True 
)

# सब्सक्राइब चेक फंक्शन
async def is_subscribed(client, message):
    try:
        await client.get_chat_member(UPDATE_CHANNEL, message.from_user.id)
        return True
    except errors.UserNotParticipant:
        await message.reply_text(
            "❌ **एक्सेस अस्वीकार!**\n\nबोट इस्तेमाल करने के लिए हमारे ग्रुप में शामिल होना अनिवार्य है।",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📢 ग्रुप जॉइन करें", url=f"https://t.me/{UPDATE_CHANNEL}")
            ]])
        )
        return False
    except Exception:
        return True

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await is_subscribed(client, message): return
    await message.reply_text(
        f"नमस्ते {message.from_user.first_name}!\n\nयूट्यूब वीडियो की लिंक भेजें और मैं उसे डाउनलोड कर दूँगा।\n\n**DOWNLOADED BY :– ➤ 𝕊𝔸ℂℍ𝕀ℕ 𝕊ℍ𝔸ℝ𝕄𝔸**"
    )

@app.on_message(filters.regex(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+") & filters.private)
async def handle_link(client, message):
    if not await is_subscribed(client, message): return
    
    url = message.text
    sent_msg = await message.reply_text("वीडियो की जानकारी निकाली जा रही है... 🔍")
    
    try:
        ydl_opts = {'cookiefile': 'cookies.txt', 'quiet': True}
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False))
        
        title = info.get('title', 'Video')
        buttons = [
            [InlineKeyboardButton("🎥 360p", callback_data=f"dl|360|{url}")],
            [InlineKeyboardButton("🎥 720p", callback_data=f"dl|720|{url}")]
        ]
        await sent_msg.edit(
            f"**🎬 शीर्षक:** {title}\n\nनीचे से क्वालिटी चुनें:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await sent_msg.edit(f"❌ एरर: {str(e)}")

@app.on_callback_query(filters.regex(r"^dl\|"))
async def download_handler(client, callback_query):
    _, quality, url = callback_query.data.split("|")
    file_name = f"video_{callback_query.from_user.id}.mp4"
    
    await callback_query.message.edit(f"📥 {quality}p डाउनलोड शुरू हो रहा है...")
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_name,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        await callback_query.message.edit("📤 टेलीग्राम पर अपलोड हो रहा है...")
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=file_name,
            caption=f"**🎬 वीडियो क्वालिटी:** {quality}p\n\n**DOWNLOADED BY :– ➤ 𝕊𝔸ℂℍ𝕀ℕ 𝕊ℍ𝔸ℝ𝕄𝔸**",
            supports_streaming=True
        )
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.message.edit(f"❌ एरर: {str(e)}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# बॉट चालू करने का तरीका
async def main():
    Thread(target=run_web, daemon=True).start()
    print("बॉट शुरू हो रहा है...")
    await app.start()
    print("बॉट चालू है!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
