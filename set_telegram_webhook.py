#!/usr/bin/env python3
"""
Script to set Telegram webhook for the bot
Run this after deploying to Render
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
RENDER_URL = "https://monqez-lifesaver.onrender.com"  # Replace with your Render URL
WEBHOOK_URL = f"{RENDER_URL}/telegram_webhook"

def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    
    data = {
        "url": WEBHOOK_URL,
        "allowed_updates": ["message"]
    }
    
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
        print(f"Webhook URL: {info.get('url', 'Not set')}")
        print(f"Pending updates: {info.get('pending_update_count', 0)}")
        if 'last_error_message':
            print(f"Last error: {info.get('last_error_message', 'None')}")

if __name__ == "__main__":
    print("Setting Telegram webhook...")
    set_webhook()
    print("\nWebhook info:")
    get_webhook_info()
