import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram.ext import Application

# 1. Render ke liye HTTP Health Check Server (Main Thread par chalega)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Dante Mechanic Bot is running 24/7!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# 2. Telegram Bot ka function
def run_telegram_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN missing!")
        return
    
    application = Application.builder().token(token).build()
    
    # Yahan apne bot ke handlers add kar lena (jaise message handler, etc.)
    # Jaise: application.add_handler(...)
    
    print("Dante Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    # Telegram Bot ko background thread mein shuru karo
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # HTTP Server ko main thread par chalao (yeh render ko port binding dega aur app band nahi hone dega)
    print(f"Starting HTTP server on port {os.environ.get('PORT', 10000)}...")
    run_server()
