import os
import glob
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "8253242144:AAGrX7Hs3e7l3sN5D2K0UPfA6VGmX10uSZk")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎵 *Namaste! Welcome to Ruivika Music Bot Join the backup channel @speedoo_bhaii_bot* 🎵\n\n"
        "Mujhe kisi bhi gaane ka naam bhejo (Jaise: `Kesariya` ya `Believer`).\n"
        "Main gaana search karke direct audio send kar doonga!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    status_msg = await update.message.reply_text(f"🔍 Searching & Downloading: *{query}*...", parse_mode="Markdown")

    base_name = f"song_{update.message.message_id}"
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': f'{base_name}.%(ext)s',
        'default_search': 'ytsearch1:',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'max_filesize': 48 * 1024 * 1024,
        # YouTube bot block bypass karne ke liye Android client spoofing:
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            song_title = info['entries'][0].get('title', query) if 'entries' in info else info.get('title', query)

        downloaded_files = glob.glob(f"{base_name}.*")
        
        if downloaded_files:
            file_path = downloaded_files[0]
            
            if os.path.getsize(file_path) > 49 * 1024 * 1024:
                await status_msg.edit_text("⚠️ Gaana 50MB se bada hai, kripya koi dusra song search karein.")
                os.remove(file_path)
                return

            await status_msg.edit_text("📤 Uploading audio to Telegram...")
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=song_title[:60],
                    performer="Ruivika Music Bot"
                )
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Gaana download nahi ho saka.")

    except Exception as e:
        err = str(e)
        if "File is larger than max_filesize" in err:
            await status_msg.edit_text("⚠️ Ye audio 50MB se bada hai, koi chhota track search karein.")
        else:
            await status_msg.edit_text(f"⚠️ Error: {err[:120]}")
            
        for f in glob.glob(f"{base_name}.*"):
            try:
                os.remove(f)
            except:
                pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, play_music))
    
    print("Ruivika Music Bot is Live...")
    app.run_polling()

if __name__ == "__main__":
    main()
