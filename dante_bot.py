import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from supabase import create_client

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

print("Starting Dante Bot...")

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"Ram Ram bhai {user_name}! 🙏 Main *Dante*, aapka Ustad Mechanic AI Companion hoon.\n\n"
        "Batao, kis bike/scooter mein lafda hai? Splendor ka current check karna hai, CDI unit ki wiring test karni hai, ya koi DTC code scan karna hai? Seedha poochho!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    print(f"Received query: {user_query}")

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
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
        print(f"Groq Error: {str(e)}")

    await update.message.reply_text(reply_text)
    print("Reply sent successfully to Telegram!")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Dante Bot is alive!")

    def log_message(self, format, *args):
        return


def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


if __name__ == "__main__":
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        exit(1)

    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    print("Starting Telegram Polling on Main Thread...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
