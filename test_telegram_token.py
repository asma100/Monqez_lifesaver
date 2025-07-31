#!/usr/bin/env python3
import requests
import json

# Test the Telegram bot token
token = "8388055974:AAEJ5V4uUG0NXpfXMJzQZ72J91Cqz9TZcWU"
url = f"https://api.telegram.org/bot{token}/getMe"

print(f"Testing token: {token}")
print(f"URL: {url}")
print("-" * 50)

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
