from datetime import timedelta
from django.utils.timezone import now
from telegram import Update
from telegram.ext import CallbackContext
import telegram
from asgiref.sync import sync_to_async

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.decorators import admin_only, send_typing_action
from users.models import User


@admin_only
async def admin(update: Update, context: CallbackContext) -> None:
    """Show help info about all secret admin commands."""
    await update.message.reply_text(static_text.secret_admin_commands)


@admin_only
async def stats(update: Update, context: CallbackContext) -> None:
    """Show user statistics asynchronously."""
    user_count = await sync_to_async(User.objects.count)()
    active_24 = await sync_to_async(User.objects.filter(updated_at__gte=now() - timedelta(hours=24)).count)()

    text = static_text.users_amount_stat.format(user_count=user_count, active_24=active_24)

    await update.message.reply_text(
        text,
        parse_mode=telegram.constants.ParseMode.HTML,
        disable_web_page_preview=True,
    )


@admin_only
@send_typing_action
async def export_users(update: Update, context: CallbackContext) -> None:
    """Exports user data as a CSV file asynchronously."""
    users = await sync_to_async(list)(User.objects.all().values())  # Convert QuerySet to a list asynchronously
    csv_users = await sync_to_async(_get_csv_from_qs_values)(users)  # Generate CSV asynchronously

    await update.message.reply_document(csv_users)
