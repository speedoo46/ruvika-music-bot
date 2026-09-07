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
        'format': 'ba/b',
        'outtmpl': f'{base_name}.%(ext)s',
        'default_search': 'ytsearch1:',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])

        downloaded_files = glob.glob(f"{base_name}.*")
        
        if downloaded_files:
            file_path = downloaded_files[0]
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=query.title(),
                    performer="Ruivika Music Bot"
                )
            os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Gaana nahi mila. Kripya doosra naam likhein.")

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error: {str(e)[:100]}")
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
