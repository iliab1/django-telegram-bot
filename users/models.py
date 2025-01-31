from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update
from telegram.ext import CallbackContext
from asgiref.sync import sync_to_async

from tgbot.handlers.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)  # Telegram user ID
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    def __str__(self):
        return f'@{self.username}' if self.username else f'{self.user_id}'

    @classmethod
    async def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """Retrieve or create a User asynchronously."""
        data = await extract_user_data_from_update(update)

        # ✅ FIXED: Ensure update_or_create runs safely in async context
        u, created = await sync_to_async(cls.objects.update_or_create, thread_sensitive=True)(
            user_id=data["user_id"], defaults=data
        )

        if created and context and context.args and len(context.args) > 0:
            payload = context.args[0]
            if str(payload).strip() != str(data["user_id"]).strip():  # ✅ Prevent self-invitation
                u.deep_link = payload
                await sync_to_async(u.save, thread_sensitive=True)()  # ✅ FIXED: Proper async save

        return u, created

    @classmethod
    async def get_user(cls, update: Update, context: CallbackContext) -> User:
        """Retrieve an existing user or create one."""
        u, _ = await cls.get_user_and_created(update, context)
        return u

    @classmethod
    async def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """Find a user by username or Telegram user ID."""
        username = str(username_or_user_id).replace("@", "").strip().lower()

        if username.isdigit():
            user = await sync_to_async(cls.objects.filter(user_id=int(username)).first, thread_sensitive=True)()
        else:
            user = await sync_to_async(cls.objects.filter(username__iexact=username).first, thread_sensitive=True)()

        return user  # ✅ FIXED: Properly returning None if user is not found

    @property
    def invited_users(self) -> QuerySet[User]:
        """Return users who joined via deep links."""
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        """Return a string representation of the user."""
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name


class Location(CreateTracker):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()

    objects = GetOrNoneManager()

    def __str__(self):
        return f"user: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"
