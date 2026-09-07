import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Aapka Bot Token
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

    file_name = f"song_{update.message.message_id}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_name,
        'default_search': 'ytsearch1:',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])

        actual_file = file_name if os.path.exists(file_name) else file_name.replace(".mp3", "") + ".mp3"

        if os.path.exists(actual_file):
            await update.message.reply_audio(
                audio=open(actual_file, 'rb'),
                title=query.title(),
                performer="Ruivika Music Bot"
            )
            os.remove(actual_file)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Gaana download nahi ho saka. Kripya dusra naam likhein.")

    except Exception as e:
        await status_msg.edit_text("⚠️ Gaana download karne me error aaya. Sahi naam dobara try karein.")
        if os.path.exists(file_name):
            os.remove(file_name)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, play_music))
    
    print("Ruivika Music Bot is Live...")
    app.run_polling()

if __name__ == "__main__":
    main()
