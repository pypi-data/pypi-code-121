import traceback
import multidict

from .http import HTTPClient
from .gateway import Gateway
from .cache import Cache
from .user import ClientUser

class Client:
    def __init__(self, intents: int = 0):
        self.intents = intents
        self._events = multidict.MultiDict()
        self._cache = Cache()

    async def from_token(self, token: str, ws: bool = False):
        self._http = HTTPClient(token)

        if ws:
            self._gateway = Gateway(token=token, client=self)
            await self._gateway.start()
        else:
            self.user = ClientUser(self, **await self._http.get_me())

    @classmethod
    async def signup(
        cls,
        email: str,
        password: str,
        username: str,
        intents: int,
        ws: bool,
        pronouns: str = None,
        bio: str = None,
        locale: str = None,
    ):
        http, _ = HTTPClient.signup(
            email=email,
            password=password,
            username=username,
            pronouns=pronouns,
            bio=bio,
            locale=locale
        )

        ret = cls(intents)
        ret._http = http

        if ws:
            ret._gateway = Gateway(token=http._token, intents=intents, client=ret)
            await ret._gateway.start()

    async def _dispatch(self, event: str, *args):
        callbacks = self._events.getall(event)

        for callback in callbacks:
            try:
                await callback(*args)
            except:
                traceback.print_exc()

    def listen(self, event: str):
        def inner(func):
            self._events.add(event, func)
            return func
        return inner
