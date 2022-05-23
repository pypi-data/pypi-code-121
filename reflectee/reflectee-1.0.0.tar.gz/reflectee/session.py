from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any, Coroutine

from .event import Event
from .exceptions import RequestException, UnexpectedError
from .handlers import handlers

if TYPE_CHECKING:
    from socketio import AsyncServer

__all__ = ["Session"]


class User:
    sid: str


class Session(object):
    def __init__(self, sio: AsyncServer, sid: str, environ, auth):

        self.sio: AsyncServer = sio
        self.sid: str = sid
        self.User = self.get_user_class()
        self.user: self.User = self.User()
        self.Event = self.get_event_class()
        self.environ = environ
        self.auth = auth
        self.event: str = None
        self.debug: bool = self.get_debug()

    def get_user_class(self):
        return User

    def get_event_class(self):
        return Event

    def get_debug(self):
        return False

    # get the room name for an user
    def get_user_room(self, user):
        return f"user.{user}"

    # join a shared room
    async def join(self, channel):
        self.sio.enter_room(self.sid, channel)

    # leave a shared room
    async def leave(self, channel):
        self.sio.leave_room(self.sid, channel)

    async def resolve_error(self, *args, **kwargs):
        await self.sio.emit(*args, **kwargs, to=self.sid, ignore_queue=True)

    # on new message from client, got event and input data
    async def on(self, handler, input):

        try:
            handler_id: list = handler.rsplit("#", 1)
            handler: str = handler_id[0]
            id: str = handler_id[1] if len(handler_id) > 1 else None
            event: self.Event = self.Event(
                self, handler=handler, input=input, id=id
            )
            callback_value = await event.call(handlers)
            if callback_value:
                # event.reflect(callback_value, resolve=True, skip=self.sid)
                return callback_value

        except RequestException as e:
            if self.debug:
                print(traceback.format_exc())
                await self.resolve_error(
                    dict(
                        input=input,
                        error=str(e),
                        traceback=traceback.format_exc(),
                    )
                )
            return dict(error=str(e))

        except Exception as e:
            if self.debug:
                print(traceback.format_exc())
                await self.resolve_error(
                    dict(
                        input=input,
                        error=str(e),
                        traceback=traceback.format_exc(),
                    )
                )
                return dict(
                    error=str(e),
                    traceback=traceback.format_exc(),
                )
            else:
                # TODO: log error
                return dict(error="Unexpected error")

    # attach user the socket session (sid)
    async def set_user(self, user) -> Coroutine[object]:
        await self.join(self.get_user_room(user))
        # set user on session
        self.user = user

    async def close(self):
        pass
