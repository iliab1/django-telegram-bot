import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')
django.setup()

from tgbot.bot_instance import application
from telegram import Update
from tgbot.dispatcher import add_handlers

def main() -> None:
    """Start the bot."""
    add_handlers(application)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()