import os
import glob
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "8253242144:AAGrX7Hs3e7l3sN5D2K0UPfA6VGmX10uSZk")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎵 *Namaste! Welcome to Ruivika Music Bot* 🎵\n\n"
        "Mujhe kisi bhi gaane ka naam bhejo (Jaise: `Kesariya` ya `Believer`).\n"
        "Main gaana search karke direct audio send kar doonga!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    status_msg = await update.message.reply_text(f"🔍 Searching & Downloading: *{query}*...", parse_mode="Markdown")

    base_name = f"song_{update.message.message_id}"
    ydl_opts = {
        # Sirf audio download karega (m4a/mp3) jo lightweight hota hai
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': f'{base_name}.%(ext)s',
        'default_search': 'ytsearch1:',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'max_filesize': 48 * 1024 * 1024, # 48 MB limit taaki Telegram reject na kare
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            song_title = info['entries'][0].get('title', query) if 'entries' in info else info.get('title', query)

        downloaded_files = glob.glob(f"{base_name}.*")
        
        if downloaded_files:
            file_path = downloaded_files[0]
            
            # File size check (< 50MB)
            if os.path.getsize(file_path) > 49 * 1024 * 1024:
                await status_msg.edit_text("⚠️ Gaana 50MB se bada hai, Telegram bot 50MB se badi file nahi bhej sakta.")
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
            await status_msg.edit_text("❌ Gaana nahi mila ya size bohot bada tha.")

    except Exception as e:
        err = str(e)
        if "File is larger than max_filesize" in err:
            await status_msg.edit_text("⚠️ Ye audio 50MB se bada hai, kripya koi chhota track try karein.")
        else:
            await status_msg.edit_text(f"⚠️ Error: {err[:100]}")
            
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
