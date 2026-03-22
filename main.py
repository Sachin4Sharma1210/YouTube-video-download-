import os
import asyncio
import time
from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# --- कॉन्फ़िगरेशन ---
API_ID = 29218807
API_HASH = "5de693a39423272c34457419323466a1"
BOT_TOKEN = "8441306868:AAFiY_FTmyljnldJq6da8NcESkH5hVXCiLA"
OWNER_ID = 7850454902
UPDATE_CHANNEL = "Sachin4Sharma1210"

app = Client("yt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- सब्सक्राइब चेक ---
async def is_subscribed(client, message):
    try:
        await client.get_chat_member(UPDATE_CHANNEL, message.from_user.id)
        return True
    except errors.exceptions.bad_request_400.UserNotParticipant:
        await message.reply_text(
            "❌ **एक्सेस अस्वीकार!**\n\nबोट का उपयोग करने के लिए हमारे ग्रुप में शामिल होना अनिवार्य है।",
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
    await message.reply_text(
        f"नमस्ते {message.from_user.first_name}!\nमुझे यूट्यूब वीडियो या प्लेलिस्ट की लिंक भेजें।\n\n"
        "**DOWNLOADED BY :– ➤ 𝕊𝔸ℂℍ𝕀ℕ 𝕊ℍ𝔸ℝ𝕄𝔸**"
    )

@app.on_message(filters.regex(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def handle_link(client, message):
    if not await is_subscribed(client, message): return
    
    url = message.text
    sent_msg = await message.reply_text("वीडियो की जानकारी प्रोसेस की जा रही है... ⏳")
    
    try:
        ydl_opts = {'cookiefile': 'cookies.txt', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            
            buttons = [
                [InlineKeyboardButton("🎥 360p", callback_data=f"dl|360|{url}")],
                [InlineKeyboardButton("🎥 720p", callback_data=f"dl|720|{url}")]
            ]
            await sent_msg.edit(
                f"**📌 शीर्षक:** {title}\n\nक्वालिटी चुनें:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        await sent_msg.edit(f"❌ एरर: {str(e)}")

@app.on_callback_query(filters.regex(r"^dl\|"))
async def download_handler(client, callback_query):
    _, quality, url = callback_query.data.split("|")
    user_id = callback_query.from_user.id
    file_name = f"video_{user_id}_{int(time.time())}.mp4"
    
    await callback_query.message.edit(f"📥 {quality}p में डाउनलोड शुरू हो रहा है... कृपया धैर्य रखें।")
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_name,
        'cookiefile': 'cookies.txt',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')

        await callback_query.message.edit("📤 टेलीग्राम पर अपलोड किया जा रहा है...")
        
        await client.send_video(
            chat_id=callback_query.message.chat.id,
            video=file_name,
            caption=f"**🎬 शीर्षक:** {title}\n\n**DOWNLOADED BY :– ➤ 𝕊𝔸ℂℍ𝕀ℕ 𝕊ℍ𝔸ℝ𝕄𝔸**",
            supports_streaming=True
        )
        await callback_query.message.delete()
    except Exception as e:
        await callback_query.message.edit(f"❌ एरर: {str(e)}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

print("Bot is Running...")
app.run()
  
