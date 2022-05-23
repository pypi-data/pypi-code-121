from typing import Callable
from threading import Lock
import asyncio
import telectron
from telectron import filters
from telectron.filters import Filter
from telectron.scaffold import Scaffold

album_messages_filter = filters.create(lambda _, __, m: m.media_group_id)

ALBUM_HACK_DELAY = 1.5


class OnAlbum(Scaffold):
    def on_album(
            self=None,
            filters=None,
            group: int = 0
    ) -> callable:

        def decorator(func: Callable) -> Callable:
            messages_filters = (self
                                if isinstance(self, Filter)
                                else filters)
            on_message_filters = (album_messages_filter & messages_filters
                                  if messages_filters
                                  else album_messages_filter)

            func = album_saver(func)

            if isinstance(self, telectron.Client):
                self.add_handler(telectron.handlers.MessageHandler(func, on_message_filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (telectron.handlers.MessageHandler(func, on_message_filters), group)
                )

            return func

        return decorator
        self.albums = TAlbums(self)
        return self.albums.on_album_messages(*args, **kwargs)

    def handle_album(self, original_handler):
        def dispatch_event(media_group_id):
            with self.album_lock:
                album = self.albums[media_group_id]
                album.messages.sort(key=lambda m: m.id)
                original_handler(self, album.messages)
                del self.albums[media_group_id]
        return dispatch_event


def album_saver(original_handler):
    def wrapper(client, message):
        with client.album_lock:
            album = client.albums.get(message.media_group_id)
            if album is None:
                client.albums[message.media_group_id] = Album(
                    client,
                    message.media_group_id,
                    client.handle_album(original_handler)
                )
                album = client.albums[message.media_group_id]
        with album.lock:
            album.add_message(message)
    return wrapper


class Album:
    def __init__(self, telegram_client, media_group_id, dispatch_event):
        self.telegram_client = telegram_client
        self.media_group_id = media_group_id
        self.dispatch_event = dispatch_event
        self.lock = Lock()
        self.messages = []
        self.due = self.telegram_client.loop.time() + ALBUM_HACK_DELAY

        telegram_client.loop.create_task(self.deliver_event())

    def add_message(self, message):
        self.messages.append(message)

        self.due = self.telegram_client.loop.time() + ALBUM_HACK_DELAY

    async def deliver_event(self):
        while True:
            diff = self.due - self.telegram_client.loop.time()
            if diff <= 0:
                self.telegram_client.loop.run_in_executor(None, self.dispatch_event, self.media_group_id)
                return

            await asyncio.sleep(diff)
