import telegram
from telegram.ext import Application

from dtb.settings import TELEGRAM_TOKEN

# Global bot application instance
application: Application = Application.builder().token(TELEGRAM_TOKEN).build()

# TODO: Add some type of check for the token