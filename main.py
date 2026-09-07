import os
import threading
from flask import Flask
import telebot
from telebot import types

# 1. Flask Dummy Server (Render ko jagaye rakhne ke liye)
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Ruvika Music Bot is Live 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# 2. Telegram Bot
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

STREAMS = {
    "lofi": {"title": "☕ 24/7 Chill Lofi Beats", "url": "https://stream.zeno.fm/f3wvbbqmdg8uv"},
    "hindi": {"title": "📻 24/7 Bollywood Hits", "url": "https://stream.zeno.fm/8wv40u8014zuv"},
    "pop": {"title": "🎧 24/7 English Pop Hits", "url": "https://stream.zeno.fm/4v60wf2014zuv"}
}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    name = message.from_user.first_name
    text = f"Namaste {name}! 🙏\nMain hoon **Ruvika Music Bot**.\nNiche se music station chunein aur 24 ghante background me suniye:"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("☕ Play Lofi Beats (24/7)", callback_data="play_lofi"),
        types.InlineKeyboardButton("📻 Play Bollywood Hits (24/7)", callback_data="play_hindi"),
        types.InlineKeyboardButton("🎧 Play English Pop (24/7)", callback_data="play_pop")
    )
    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_click(call):
    key = call.data.replace("play_", "")
    if key in STREAMS:
        station = STREAMS[key]
        msg = f"🎵 **Playing: {station['title']}**\n\n🔗 Sunne ke liye yahan click karein:\n{station['url']}"
        bot.answer_callback_query(call.id, text="Starting stream...")
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print("Ruvika Music Bot running...")
    bot.infinity_polling(none_stop=True)