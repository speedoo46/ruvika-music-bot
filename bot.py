import os
import requests
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "8253242144:AAGrX7Hs3e7l3sN5D2K0UPfA6VGmX10uSZk")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎵 *Namaste! Welcome to Ruivika Music Bot Join the backup channel @speedoo_bhaii_bot* 🎵\n\n"
        "Mujhe kisi bhi gaane ka naam bhejo (Jaise: `Sanam Teri Kasam` ya `Believer`).\n"
        "Main 2 second me direct original MP3 send kar doonga!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

def search_saavn(query):
    try:
        url = f"https://saavn.dev/api/search/songs?query={requests.utils.quote(query)}"
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("success") and data.get("data", {}).get("results"):
            song = data["data"]["results"][0]
            title = song.get("name", query)
            artist = song.get("primaryArtists", "Ruivika Music")
            
            # Highest quality audio download URL (320kbps / 160kbps)
            download_urls = song.get("downloadUrl", [])
            audio_url = download_urls[-1].get("url") if download_urls else None
            return title, artist, audio_url
    except Exception:
        pass
    return None, None, None

async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    status_msg = await update.message.reply_text(f"🔍 Searching: *{query}*...", parse_mode="Markdown")

    file_name = f"song_{update.message.message_id}.mp3"

    try:
        # 1. Pehle JioSaavn se high-speed original track try karein (No cloud IP block)
        title, artist, audio_url = search_saavn(query)

        if audio_url:
            await status_msg.edit_text(f"⬇️ Downloading: *{title}*...", parse_mode="Markdown")
            r = requests.get(audio_url, stream=True, timeout=30)
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            await status_msg.edit_text("📤 Sending to Telegram...")
            with open(file_name, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=title,
                    performer=artist
                )
            if os.path.exists(file_name):
                os.remove(file_name)
            await status_msg.delete()
            return

        # 2. Agar Saavn par na mile toh SoundCloud fallback
        await status_msg.edit_text("🔍 Searching on Alternative Servers...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_name,
            'default_search': 'scsearch1:',
            'noplaylist': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])

        if os.path.exists(file_name):
            await status_msg.edit_text("📤 Sending to Telegram...")
            with open(file_name, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=query.title(),
                    performer="Ruivika Music Bot"
                )
            os.remove(file_name)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Gaana nahi mila. Kripya sahi spelling ke sath likhein.")

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Error: Gaana fetch nahi ho saka, kripya dobara try karein.")
    finally:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
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
