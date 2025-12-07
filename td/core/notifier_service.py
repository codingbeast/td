"""td/core/notifier_service.py"""
# pylint: disable = W0603
import os
from td.core.logging.telegram import TelegramNotifier


_NOTIFIER  = None

def get_notifier():
    """Return global notifier instance (lazy initialized)."""
    global _NOTIFIER
    if _NOTIFIER is None:
        _NOTIFIER = TelegramNotifier(
            token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_USER_ID"),
        )
    return _NOTIFIER
