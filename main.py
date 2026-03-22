import os
import asyncio
import time
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
from flask import Flask
from threading import Thread

# --- Flask Server (Render को जगाए रखने के लिए) ---
web_app = Flask(__name__)
@web_app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    # Render हमेशा एक PORT एन्वायरमेंट वेरिएबल देता है
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- बॉट कॉन्फ़िगरेशन ---
API_ID = 29218807
API_HASH = "5de693a39423272c34457419323466a1"
BOT_TOKEN = "8441306868:AAFiY_FTmyljnldJq6da8NcESkH5hVXCiLA"
OWNER_ID = 7850454902
UPDATE_CHANNEL = "Sachin4Sharma1210"

app = Client("yt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# सब्सक्राइब चेक करने का फंक्शन
async def is_subscribed(client, message):
    try:
        await client.get_chat_member(UPDATE_CHANNEL, message.from_user.id)
        return True
    except errors.exceptions.bad_request_400.UserNotParticipant:
        await message.reply_text(
            "❌ **एक्सेस अस्वीकार!**\n\nबोट इस्तेमाल करने के लिए हमारे ग्रुप में शामिल हों।",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📢 ग्रुप जॉइन करें", url=f"https://t.me/{UPDATE_CHANNEL}")
            ]])
        )
        return False
    except Exception:
        return True

@app.on_message(filters.command("start"))
async def start(client, message):
    if not await is_subscribed(client, message): return
    await message.reply_text(f"नमस्ते {message.from_user.first_name}!\nलिंक भेजें।\n\n**DOWNLOADED BY :– ➤ 𝕊𝔸ℂℍ𝕀ℕ 𝕊ℍ𝔸ℝ𝕄𝔸**")

@app.on_message(filters.regex(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def handle_link(client, message):
    if not await is_subscribed(client, message): return
    url = message.text
    sent_msg = await message.reply_text("प्रोसेसिंग... ⏳")
    
    try:
        ydl_opts = {'cookiefile': 'cookies.txt', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            buttons = [
                [InlineKeyboardButton("🎥 360p", callback_data=f"dl|360|{url}")],
                [InlineKeyboardButton("🎥 720p", callback_data=f"dl|720|{url}")]
            ]
            await sent_msg.edit(f"**📌 शीर्षक:** {title}\n\nक्वालिटी चुनें:", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await sent_msg.edit(f"❌ एरर: {str(e)}")

@app.on_callback_query(filters.regex(r"^dl\|"))
async def download_handler(client, callback_query):
    _, quality, url = callback_query.data.split("|")
    file_name = f"video_{callback_query.from_user.id}_{int(time.time())}.mp4"
    await callback_query.message.edit(f"📥 {quality}p डाउनलोड शुरू...")
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_name,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
    }

    try:
        # यहाँ 'run_in_executor' का इस्तेमाल कर रहे हैं ताकि इवेंट लूप ब्लॉक न हो
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        await callback_query.message.edit("📤 अपलोड हो रहा है...")
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=file_name,
            caption=f"**🎬 शीर्षक:** क्वालिटी - {quality}p\n\n**DOWNLOADED BY :– ➤ 𝕊𝔸ℂℍ𝕀ℕ 𝕊ℍ𝔸ℝ𝕄𝔸**",
            supports_streaming=True
        )
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.message.edit(f"❌ एरर: {str(e)}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# --- बॉट शुरू करने का नया तरीका (Python 3.12+ Fix) ---
async def main():
    # Flask को अलग थ्रेड में चलाना
    Thread(target=run_web, daemon=True).start()
    print("Bot is starting...")
    await app.start()
    print("Bot is Running!")
    # बॉट को चालू रखने के लिए
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

