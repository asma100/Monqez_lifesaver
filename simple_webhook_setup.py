#!/usr/bin/env python3
"""
Simple script to set Telegram webhook (no dependencies)
"""

import requests
import json

# Configuration - Replace with your actual values
TELEGRAM_TOKEN = "8388055974:AAEJ5V4uUG0NXpfXMJzQZ72J91Cqz9TZcWU"
RENDER_URL = "https://monqez-lifesaver.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/telegram_webhook"

def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    
    data = {
        "url": WEBHOOK_URL,
        "allowed_updates": ["message"]  # Include location updates
    }
    
    print(f"Setting webhook to: {WEBHOOK_URL}")
    print("-" * 50)
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print(f"✅ Webhook set successfully!")
            print(f"Webhook URL: {WEBHOOK_URL}")
        else:
            print(f"❌ Error: {result['description']}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

def get_webhook_info():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    response = requests.get(url)
    
    if response.status_code == 200:
        info = response.json()['result']
        print(f"Current webhook URL: {info.get('url', 'Not set')}")
        print(f"Pending updates: {info.get('pending_update_count', 0)}")
        if info.get('last_error_message'):
            print(f"Last error: {info.get('last_error_message')}")
        else:
            print("No errors!")

if __name__ == "__main__":
    print("🤖 Setting Telegram webhook...")
    set_webhook()
    print("\n📊 Current webhook info:")
    get_webhook_info()
    print("\n🎉 Done! Your bot should now work on Telegram!")
    print("💬 Try messaging @monqez_lifesaver_bot on Telegram")
