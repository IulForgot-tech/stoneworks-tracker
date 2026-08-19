import os
import json
import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# =========================================================================
# 🛠️ YOUR WEBHOOK LINK IS READY TO GO HERE
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1539575319592439890/Ce20OKXJ5oLglpL8plmpbQlxQYvxtf_KRZc1oCNeaxYaAtIp8AkbwnjYYnfTR_G467Z4"
# =========================================================================

MAP_DATA_URL = "https://stoneworks.gg"
CACHE_FILE = "previous_claims.json"

class SimpleWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Stoneworks Tracker Bot is Active and Healthy!")
    def log_message(self, format, *args):
        return

def run_fake_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleWebHandler)
    server.serve_forever()

def send_discord_notification(title, description, color):
    print(f"🔄 Transmitting payload to Discord Forum: {title}...")
    
    # We add 'thread_name' so Discord automatically spins up a clean thread in your forum channel!
    payload = {
        "thread_name": "Stoneworks Live Map Logs",
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
                "footer": {"text": "Stoneworks Abexilas Map Tracker"},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        ]
    }
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print(f"📊 Discord Server Response: {r.status_code}")
    except Exception as e:
        print(f"🚨 Network error: {e}")

def check_for_changes():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(MAP_DATA_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            return
        data = response.json()
    except Exception as e:
        print(f"Connection update failed: {e}")
        return

    current_claims = {}
    if data and 'sets' in data:
        for set_id, set_data in data['sets'].items():
            areas = set_data.get('areas', {})
            for area_id, area_info in areas.items():
                label = area_info.get('label', 'Unnamed Claim').replace("<br />", " ").strip()
                current_claims[area_id] = {'label': label}

    if not os.path.exists(CACHE_FILE):
        print(f"Initial setup complete. Saved baseline database with {len(current_claims)} active towns.")
        send_discord_notification("🤖 System Status", f"Online! Successfully cached {len(current_claims)} active towns from the Stoneworks map.", 255)
        with open(CACHE_FILE, 'w') as f:
            json.dump(current_claims, f)
        return

    with open(CACHE_FILE, 'r') as f:
        previous_claims = json.load(f)

    for claim_id, info in current_claims.items():
        if claim_id not in previous_claims:
            send_discord_notification("✨ New Claim Registered", f"**Town/Claim:** {info['label']}\n**Marker ID:** `{claim_id}`", 65280)

    for claim_id, info in previous_claims.items():
        if claim_id not in current_claims:
            send_discord_notification("❌ Claim Unregistered / Fallen", f"**Town/Claim:** {info['label']}\n**Marker ID:** `{claim_id}`", 16711680)

    with open(CACHE_FILE, 'w') as f:
        json.dump(current_claims, f)

if __name__ == "__main__":
    print("Tracker initializing...")
    web_thread = threading.Thread(target=run_fake_web_server, daemon=True)
    web_thread.start()
    
    check_for_changes()
    
    while True:
        time.sleep(300)
        check_for_changes()

