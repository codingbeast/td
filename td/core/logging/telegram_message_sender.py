"""td/core/broker/logging/telegram_message_sender.py"""
import requests

def send_message(telegram_bot, chat_id, message):
    """
    Sends a message to a Telegram chat using the Telegram Bot API.

    Args:
        telegram_bot (str): The Telegram Bot API token.
        chat_id (str): The ID of the chat where the message will be sent.
        message (str): The message to be sent.

    Returns:
        bool: True if the message is sent successfully, False otherwise.
    """
    url = f'https://api.telegram.org/bot{telegram_bot}/sendMessage'
    # Payload for the request
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, json=payload, timeout=20)
    if response.status_code == 200:
        print('Message sent successfully!')
        return True
    else:
        print('Failed to send the message. Status code:', response.status_code)
        print('Response:', response.text)
        return False
