import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 1. Render ke liye dummy web server jo port bind karega
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Dante Mechanic Bot is running 24/7!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# 2. Server ko background thread mein start kar do
threading.Thread(target=run_server, daemon=True).start()
