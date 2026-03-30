import os
import threading
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from flask import Flask

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

SYSTEM_PROMPT = """Tu ek helpful AI assistant hai.
Hinglish mein jawab de.
Short aur clear jawab de.
RAS exam, education aur general topics pe help kar."""

def ask_gemini(user_msg):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser: {user_msg}"}]
        }]
    }
    response = requests.post(url, json=payload)
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    try:
        reply = ask_gemini(user_msg)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Sorry, abhi kuch problem hai!")

def main():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
  print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
