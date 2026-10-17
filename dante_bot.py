import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from supabase import create_client

print("Initializing Dante Bot Script...")

# 1. Initialize Clients
groq_api_key = os.environ.get("GROQ_API_KEY")
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")

print(f"GROQ_API_KEY present: {bool(groq_api_key)}")
print(f"TELEGRAM_BOT_TOKEN present: {bool(telegram_token)}")

groq_client = Groq(api_key=groq_api_key)
supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# 2. Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    print(f"Received /start command from {user_name}")
    welcome_text = (
        f"Ram Ram bhai {user_name}! 🙏 Main **Dante**, aapka Ustad Mechanic AI Companion hoon.\n\n"
        "Batao, kis bike/scooter mein lafda hai? Splendor ka current check karna hai, CDI unit ki wiring test karni hai, ya koi DTC code scan karna hai? Seedha poochho!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    print(f"--> Received text message: {user_query}")
    
    try:
        print("Calling Groq API...")
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Dante, an expert Indian two-wheeler mechanic AI assistant (Ustad Mechanic style, Hinglish expert, specializing in Hero Splendor, HF Deluxe, Honda Activa, Bajaj Pulsar, EV diagnostics, wiring, sensors, and ECU troubleshooting)."
                },
                {
                    "role": "user", 
                    "content": user_query
                }
            ],
            temperature=0.7
        )
        reply_text = response.choices[0].message.content
        print(f"Groq Response generated successfully. Length: {len(reply_text)}")
    except Exception as e:
        reply_text = f"Bhai, error aa gaya Groq se: {str(e)}"
        print(f"ERROR in Groq API: {str(e)}")

    print("Sending reply back to Telegram...")
    await update.message.reply_text(reply_text)
    print("Reply sent successfully!")

# 3. Render HTTP Health Check Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Dante Mechanic Bot is running 24/7 with Groq!")
    
    def log_message(self, format, *args):
        return  # Keep logs clean

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"HTTP server successfully bound to port {port}")
    server.serve_forever()

# 4. Telegram Bot Runner (Background Thread)
def run_telegram_bot():
    if not telegram_token:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        return
    
    print("Building Telegram Application...")
    application = Application.builder().token(telegram_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Starting Telegram Bot Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    print("Starting Background Telegram Bot Thread...")
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    print("Starting Main Thread HTTP Server...")
    run_server()
