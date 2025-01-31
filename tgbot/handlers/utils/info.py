from typing import Dict, Any
from telegram import Update


async def extract_user_data_from_update(update: Update) -> Dict[str, Any]:
    """
    Extracts user data from a python-telegram-bot `Update` instance.
    """
    user = update.effective_user

    if not user:
        return {}  # Return empty dict if no user data is available

    return {
        "user_id": user.id,
        "is_blocked_bot": False,
        "username": user.username or None,
        "first_name": user.first_name or None,
        "last_name": user.last_name or None,
        "language_code": user.language_code or None,
    }