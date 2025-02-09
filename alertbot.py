import requests

def send_telegram_notification(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print("Failed to send notification.")

# Usage
# bot_token = '7722089045:AAE8jSa8wDVSD4CX6Lf-CulEk8aFpxLUgLg'
# chat_id = '617451765'
# message = 'ALERT!!!'
# send_telegram_notification(bot_token, chat_id, message)