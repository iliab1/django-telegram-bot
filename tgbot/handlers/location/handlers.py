import telegram
from telegram import Update
from telegram.ext import CallbackContext
from asgiref.sync import sync_to_async

from tgbot.handlers.location.static_text import share_location, thanks_for_location
from tgbot.handlers.location.keyboards import send_location_keyboard
from users.models import User, Location


async def ask_for_location(update: Update, context: CallbackContext) -> None:
    """Handles the /ask_location command asynchronously."""
    u = await User.get_user(update, context)

    await context.bot.send_message(
        chat_id=u.user_id,
        text=share_location,
        reply_markup=send_location_keyboard()
    )


async def location_handler(update: Update, context: CallbackContext) -> None:
    """Handles the received location asynchronously."""
    u = await User.get_user(update, context)
    lat, lon = update.message.location.latitude, update.message.location.longitude

    # Save location asynchronously
    await sync_to_async(Location.objects.create)(user=u, latitude=lat, longitude=lon)

    await update.message.reply_text(
        thanks_for_location,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
