import os
import json
import time
import requests

# 1. MAKE SURE YOUR WEBHOOK IS PASTED PERFECTLY BETWEEN THESE QUOTES
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1539575319592439890/Ce20OKXJ5oLglpL8plmpbQlxQYvxtf_KRZc1oCNeaxYaAtIp8AkbwnjYYnfTR_G467Z4E"

MAP_DATA_URL = "https://map.stoneworks.gg/abex/#minecraft_overworld;flat;64,64,48;3"
CACHE_FILE = "previous_claims.json"

def send_discord_notification(title, description, color):
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print(f"📡 LOG: {title} - {description}")
        return
    payload = {
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
        print(f"Discord response code: {r.status_code} (204 means successful!)")
    except Exception as e:
        print(f"Error connecting to Discord: {e}")

def check_for_changes():
    print("Attempting to connect to the Stoneworks server data...")
    try:
        # We add a common web browser header so the Stoneworks map server doesn't block PythonAnywhere
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(MAP_DATA_URL, headers=headers, timeout=15)
        print(f"Stoneworks server response code: {response.status_code}")

        if response.status_code != 200:
            print("Stoneworks map data is temporarily unavailable or blocking the connection.")
            return
        data = response.json()
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    current_claims = {}
    if data and 'sets' in data:
        for set_id, set_data in data['sets'].items():
            areas = set_data.get('areas', {})
            for area_id, area_info in areas.items():
                label = area_info.get('label', 'Unnamed Claim').replace("<br />", " ").strip()
                current_claims[area_id] = {'label': label}

    # FOR THE TEST: We force it to tell us it's working immediately
    if not os.path.exists(CACHE_FILE):
        print(f"Successfully connected! Creating local map baseline with {len(current_claims)} towns.")
        send_discord_notification("🤖 Tracker Status", f"Online! Successfully cached {len(current_claims)} active towns from the Stoneworks map.", 255)
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
    # Run once right away
    check_for_changes()

    # Keep running every 5 minutes
    while True:
        print("Sleeping for 5 minutes before checking for updates...")
        time.sleep(300)
        check_for_changes()
