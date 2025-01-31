from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# Import handlers
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON

# Import handlers
from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers

# ✅ Function to add handlers
def add_handlers(application: Application) -> None:
    """Registers all bot handlers."""
    # ✅ Onboarding
    application.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # ✅ Admin commands
    application.add_handler(CommandHandler("admin", admin_handlers.admin))
    application.add_handler(CommandHandler("stats", admin_handlers.stats))
    application.add_handler(CommandHandler("export_users", admin_handlers.export_users))

    # ✅ Location
    application.add_handler(CommandHandler("ask_location", location_handlers.ask_for_location))
    application.add_handler(MessageHandler(filters.LOCATION, location_handlers.location_handler))

    # ✅ Secret level (callback button)
    application.add_handler(CallbackQueryHandler(onboarding_handlers.secret_level, pattern=f"^{SECRET_LEVEL_BUTTON}"))

    # ✅ Broadcast message
    application.add_handler(
        MessageHandler(filters.Regex(rf'^{broadcast_command}(/s)?.*'),
                       broadcast_handlers.broadcast_command_with_message)
    )
    application.add_handler(
        CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler, pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    )

    # ✅ File ID retrieval (for animations)
    application.add_handler(MessageHandler(filters.ANIMATION, files.show_file_id))

    # ✅ Error handling
    application.add_error_handler(error.send_stacktrace_to_tg_chat)

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return application