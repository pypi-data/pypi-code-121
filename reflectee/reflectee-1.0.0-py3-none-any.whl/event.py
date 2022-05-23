from __future__ import annotations

from typing import TYPE_CHECKING, Any, Coroutine

if TYPE_CHECKING:
    from .session import Session

from .exceptions import BadRequest, NotAuthorized, NotFound

__all__ = ["Event"]


class Event:

    BadRequest = BadRequest
    NotFound = NotFound
    NotAuthorized = NotAuthorized

    def __init__(
        self,
        session: Session,
        handler: str,
        input: Any = None,
        id: str | None = None,
    ):
        self.session: Session = session
        self.handler: str = handler
        self.id: str | None = id
        self.data: Any = input

    @property
    def user(self):
        return self.session.user

    @property
    def User(self):
        return self.session.User

    async def call(self, handlers):
        if self.handler in handlers:
            return await handlers[self.handler](self)
        else:
            raise self.BadRequest(f"handler {self.handler} not found")

    # emit message to all user me session via rooms, includes this socket session
    async def dispatch_me(self, *args, **kwargs) -> Coroutine[Any]:
        return await self.dispatch(*args, **kwargs, resolve=self.user)

    # emit message to all user me session via rooms, except this socket session
    async def dispatch_other_me(self, *args, **kwargs) -> Coroutine[Any]:
        return await self.dispatch(
            *args, **kwargs, resolve=self.user, skip=self.session.sid
        )

    # emit message to all user session via rooms, except this socket session
    async def dispatch_user(self, user, *args, **kwargs) -> Coroutine[Any]:
        to = user if isinstance(user, self.session.User) else self.user
        return await self.dispatch(*args, to=to, **kwargs)

    # emit message to all user in session via rooms
    async def broadcast(self, *args, **kwargs) -> Coroutine[Any]:
        return await self.reflect(*args, **kwargs, broadcast=True)

    async def resolve(self, *args, **kwargs) -> Coroutine[Any]:
        # Return the data for direct socket callback and ignore self SID for other dispatching
        # usefull for exemple to broacast something at the end of handler and send the callback int a fastest way to the user
        # return await event.resolve({ ...something... }, broadcast=True)
        return await self.reflect(
            *args, **kwargs, resolve=True, skip=self.session.sid
        )

    # dispatch message to any kind of
    async def reflect(
        self,
        data: Any,
        event: str = None,
        id=None,
        to=None,
        resolve: bool = False,
        broadcast: bool = False,
        ignore_self=False,
        skip=None,
    ) -> Coroutine[Any]:

        if not isinstance(event, str):
            event = self.handler
        # TODO: verify the handlers existence

        if not isinstance(id, (str, int)):
            id = self.id

        if id:
            event = f"{event}#{id}"

        if resolve:
            ignore_queue = True
        else:
            ignore_queue = False

        if ignore_self:
            skip = self.session.sid

        if broadcast:
            to = None
        else:
            if to:
                to = await self.resolve_reflect_to(to)
            else:
                to = self.session.sid

        args = [event, data]
        kwargs = {"to": to, "ignore_queue": ignore_queue, "skip_sid": skip}

        await self.session.sio.emit(*args, **kwargs)
        return data

    async def resolve_reflect_to(self, to) -> Coroutine[Any]:
        return to

    async def set_user(self, *args, **kwargs) -> Coroutine[Any]:
        await self.session.set_user(*args, **kwargs)
