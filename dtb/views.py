import json
import logging
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from telegram import Update
from asgiref.sync import sync_to_async
from dtb.celery import app
from dtb.settings import DEBUG
from tgbot.bot_instance import application  # PTB v20+ uses `application`

logger = logging.getLogger(__name__)

@app.task(ignore_result=True)
def process_telegram_event(update_json):
    """ Process incoming Telegram updates asynchronously using Celery """
    if not application:
        logger.error("🚨 Telegram Application is not initialized!")
        return

    try:
        update = Update.de_json(update_json, application.bot)
        application.process_update(update)
    except Exception as e:
        logger.error(f"❌ Error processing Telegram update: {e}")

async def async_process_telegram_event(update_json):
    """ Async wrapper for Celery task (used in DEBUG mode) """
    await sync_to_async(process_telegram_event)(update_json)

def index(request):
    """ Debug endpoint to confirm webhook availability """
    return JsonResponse({"message": "Webhook is working!"})

class TelegramBotWebhookView(View):
    """ Django view to handle Telegram Webhook """

    async def post(self, request, *args, **kwargs):
        """ Handle incoming Telegram updates """
        try:
            update_json = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.error("🚨 Received invalid JSON payload!")
            return HttpResponseBadRequest("Invalid JSON received")

        if DEBUG:
            await async_process_telegram_event(update_json)  # Direct async processing
        else:
            process_telegram_event.delay(update_json)  # Celery processing in production

        return JsonResponse({"ok": "POST request processed"})

    async def get(self, request, *args, **kwargs):
        """ Debugging: Check if the webhook is reachable """
        return JsonResponse({"status": "Webhook is working!"})
