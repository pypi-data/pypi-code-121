import json
from datetime import date, datetime
from uuid import UUID
import django
import socketio
from django.core.asgi import get_wsgi_application
from asgiref.sync import async_to_sync

django.setup()
from ..server import Server
from django.conf import settings

redis_url = getattr(settings, 'REFLECTEE_REDIS_URL', getattr(settings, 'REDIS_URL', None))

if redis_url:
    client_manager = socketio.AsyncRedisManager(redis_url)
else:
    client_manager = None

sessions = {}

sio: socketio.AsyncServer = socketio.AsyncServer(
    # aiohttp
    # asgi
    async_mode="asgi",
    client_manager=client_manager,
    cors_allowed_origins="*",
    # engineio_logger=False,
    # logger=settings.DEBUG,
)

@sio.event
async def connect(sid, environ, auth):
    from ..utils import Session
    sessions[sid] = Session(sio, sid, environ, auth)

@sio.event
async def disconnect(sid):
    await sessions[sid].close()
    del sessions[sid]


@sio.on("*")
async def catch_all(event, sid, data):
    return await sessions[sid].on(event, data)


async def emit(*args, **kwargs):
    await sio.emit(*args, **kwargs)

def emit_sync(*args, **kwargs):
    async_to_sync(sio.emit)(*args, **kwargs)


sio = Server(redis_url=redis_url)
app: socketio.WSGIApp = socketio.WSGIApp(sio, get_wsgi_application())
