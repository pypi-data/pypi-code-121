from __future__ import annotations

from typing import TYPE_CHECKING, Coroutine

from django.conf import settings
from django.contrib.auth import get_user_model

from ..session import Session as SessionBase
from .event import Event

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    # User = get_user_model()

__all__ = ["Session"]


class Session(SessionBase):
    def get_event_class(self):
        return Event

    def get_user_class(self):
        return get_user_model()

    def get_user_room(self, user):
        return f"user.{user.pk}"

    def get_debug(self):
        return settings.DEBUG

    # attach user the socket session (sid)
    async def set_user(self, user, **kwargs) -> Coroutine[User]:

        # if user exist and already connected to an other user room (few chance.. but for hacking safety)
        if not user.is_anonymous:
            if self.user.pk != getattr(user, "pk", None):
                await self.leave(self.get_user_room(self.user))
            # if user exist and real, join his own private room
            await self.join(self.get_user_room(user))

            if user.is_staff:
                await self.join("users.staff")

            if user.is_admin:
                await self.join("users.admin")

            if user.is_superadmin:
                await self.join("users.superadmin")

        await super().set_user(user, **kwargs)
