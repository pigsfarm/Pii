import os
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from flask import Flask

# Config
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# Flask app (UptimeRobot ke liye)
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# Bot ka system prompt — customize kar sakte ho
SYSTEM_PROMPT = """Tu ek helpful AI assistant hai.
Hinglish mein jawab de (Hindi + English mix).
Short aur clear jawab de.
RAS exam, education aur general topics pe help kar."""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser: {user_msg}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Sorry, abhi kuch problem hai. Thodi der baad try karo!")

def main():
    # Flask ko alag thread mein chalao
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Bot chalao
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
