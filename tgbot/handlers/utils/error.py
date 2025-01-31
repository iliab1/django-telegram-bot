import logging
import traceback
import html
from asgiref.sync import sync_to_async

import telegram
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import TELEGRAM_LOGS_CHAT_ID
from users.models import User


async def send_stacktrace_to_tg_chat(update: Update, context: CallbackContext) -> None:
    """
    Asynchronously logs errors and notifies the user & admin.
    """

    # Fetch user asynchronously
    u = await User.get_user(update, context)

    # Log error in console
    logging.error("Exception while handling an update:", exc_info=context.error)

    # Format traceback string
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Prevent exceeding Telegram's 4096 character message limit
    truncated_tb = tb_string[:4000]  # Leave space for message text

    # Build the message with markup
    message = (
        f'An exception occurred while handling an update:\n'
        f'<pre>{html.escape(truncated_tb)}</pre>'
    )

    user_message = """
😔 Something broke inside the bot.
We are constantly improving our service, but sometimes we miss testing basic things.
We already received all the details to fix the issue.
Return to /start
"""

    # Send error message to user
    await context.bot.send_message(
        chat_id=u.user_id,
        text=user_message,
    )

    # Send error message to admin (if configured)
    admin_message = f"⚠️⚠️⚠️ Error for {u.tg_str}:\n{message}"

    if TELEGRAM_LOGS_CHAT_ID:
        await context.bot.send_message(
            chat_id=TELEGRAM_LOGS_CHAT_ID,
            text=admin_message[:4090],  # Ensure it doesn't exceed 4096 chars
            parse_mode=telegram.constants.ParseMode.HTML,
        )
    else:
        logging.error(admin_message)
