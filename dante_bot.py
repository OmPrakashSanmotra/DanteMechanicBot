import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from supabase import create_client

# 1. Initialize Gemini & Supabase Clients
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}
# Using Gemini Flash for fast & smart responses
gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are Dante, an expert Indian two-wheeler mechanic AI assistant (Ustad Mechanic style, Hinglish expert, specializing in Hero Splendor, HF Deluxe, Honda Activa, Bajaj Pulsar, EV diagnostics, wiring, sensors, and ECU troubleshooting)."
)

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
        # Generate response using Gemini API
        response = gemini_model.generate_content(user_query)
        reply_text = response.text
    except Exception as e:
        reply_text = f"Bhai, error aa gaya Gemini se: {str(e)}"

    await update.message.reply_text(reply_text)

# 3. Render HTTP Health Check Server (Background Thread)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Dante Mechanic Bot is running 24/7 with Gemini API!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Starting HTTP server on port {port}...")
    server.serve_forever()

if __name__ == "__main__":
    # HTTP Server ko background thread mein chalao (Render port binding ke liye)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Telegram Bot ko Main Thread par chalao
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        exit(1)
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Dante Bot is starting polling with Gemini on Main Thread...")
    application.run_polling()
