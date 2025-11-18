# td/core/logging/telegram.py
import requests
import os
from typing import Optional

class TelegramNotifier:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier
        Args:
            token: Telegram bot token (default: from TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID (default: from TELEGRAM_USER_ID env var)
        """
        self.token = token
        self.chat_id = chat_id
        
        if not self.token or not self.chat_id:
            raise ValueError("Telegram token and chat ID must be provided or set as environment variables")

    def send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False