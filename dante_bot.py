import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from supabase import create_client

# 1. Initialize Groq & Supabase Clients
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# 2. Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"Ram Ram bhai {user_name}! 🙏 Main **Dante**, aapka Ustad Mechanic AI Companion hoon.\n\n"
        "Batao, kis bike/scooter mein lafda hai? Splendor ka current check karna hai, CDI unit ki wiring test karni hai, ya koi DTC code scan karna hai? Seedha poochho!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    print(f"Received query: {user_query}")
    
    try:
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
    except Exception as e:
        reply_text = f"Bhai, error aa gaya Groq se: {str(e)}"

    await update.message.reply_text(reply_text)

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
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Dante Bot is starting polling in background thread...")
    application.run_polling()

if __name__ == "__main__":
    # Telegram Bot ko background thread mein chalao
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # HTTP Server ko Main Thread par chalao taaki Render ka port scan instant pass ho jaye!
    run_server()
