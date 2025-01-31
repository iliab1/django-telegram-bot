import logging
from typing import Union, Optional, Dict, List

import telegram
from telegram import MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from dtb.settings import TELEGRAM_TOKEN
from users.models import User
from tgbot.bot_instance import application

# ✅ Configure logging
logger = logging.getLogger(__name__)

async def from_celery_markup_to_markup(
    celery_markup: Optional[List[List[Dict]]] = None
) -> Optional[InlineKeyboardMarkup]:
    """ Convert Celery-formatted inline keyboard markup to Telegram format. """
    if not celery_markup:
        return None

    markup = [
        [
            InlineKeyboardButton(
                text=button["text"],
                callback_data=button.get("callback_data"),
                url=button.get("url"),
            )
            for button in row_of_buttons
        ]
        for row_of_buttons in celery_markup
    ]

    return InlineKeyboardMarkup(markup)


async def from_celery_entities_to_entities(
    celery_entities: Optional[List[Dict]] = None
) -> Optional[List[MessageEntity]]:
    """ Convert Celery-formatted message entities to Telegram format. """
    if not celery_entities:
        return None

    return [
        MessageEntity(
            type=entity["type"],
            offset=entity["offset"],
            length=entity["length"],
            url=entity.get("url"),
            language=entity.get("language"),
        )
        for entity in celery_entities
    ]


async def send_one_message(
    user_id: Union[str, int],
    text: str,
    parse_mode: Optional[str] = ParseMode.HTML,
    reply_markup: Optional[List[List[Dict]]] = None,
    reply_to_message_id: Optional[int] = None,
    disable_web_page_preview: Optional[bool] = None,
    entities: Optional[List[MessageEntity]] = None,
) -> bool:
    """
    Send a single message to a user asynchronously.

    Args:
        user_id (Union[str, int]): The recipient's user ID.
        text (str): The message content.
        parse_mode (Optional[str]): Formatting mode (default: HTML).
        reply_markup (Optional[List[List[Dict]]]): Optional keyboard markup.
        reply_to_message_id (Optional[int]): Optional message reply ID.
        disable_web_page_preview (Optional[bool]): Disable web preview.
        entities (Optional[List[MessageEntity]]): Optional message entities.

    Returns:
        bool: Whether the message was sent successfully.
    """
    bot = application.bot  # ✅ Use application's bot instance

    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        )
        await User.objects.filter(user_id=user_id).aupdate(is_blocked_bot=False)
        return True
    except telegram.error.Forbidden: # Replaced Unauthorized by Forbidden
        logger.warning(f"Cannot send message to {user_id}. Reason: Bot was stopped.")
        await User.objects.filter(user_id=user_id).aupdate(is_blocked_bot=True)
        return False
    except Exception as e:
        logger.error(f"Failed to send message to {user_id}: {e}")
        return False
