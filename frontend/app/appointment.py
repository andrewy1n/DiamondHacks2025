import requests

API_URL = "https://1c26-128-54-18-77.ngrok-free.app/appointments"
JWT_TOKEN = "your_long_jwt_token_here"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}"
}

data = {
    "date": "2025-06-30T20:55:05.926275+00:00",
    "name": "Default Test",
    "note_id": "",
    "transcript_id": ""
}

response = requests.get(API_URL, headers=headers)

if response.status_code == 200:
    print("✅ User Info:")
    print(response.json())
else:
    print(f"❌ Error {response.status_code}: {response.text}")
