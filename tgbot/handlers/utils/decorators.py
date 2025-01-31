from functools import wraps
from typing import Callable
from asgiref.sync import sync_to_async
import telegram
from telegram import Update
from telegram.ext import CallbackContext

from users.models import User


def admin_only(func: Callable):
    """
    Async Admin-only decorator.
    Used for handlers that only admins have access to.
    """

    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = await User.get_user(update, context)  # Fetch user asynchronously

        if not user.is_admin:
            return  # Ignore command if not an admin

        return await func(update, context, *args, **kwargs)

    return wrapper


def send_typing_action(func: Callable):
    """
    Sends a typing action while processing a command (async).
    """

    @wraps(func)
    async def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=telegram.constants.ChatAction.TYPING
        )  # Async send action

        return await func(update, context, *args, **kwargs)

    return command_func
