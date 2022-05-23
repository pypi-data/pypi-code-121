import json
import os
from datetime import date, datetime
from uuid import UUID

import socketio
from asgiref.sync import async_to_sync

from .django.session import Session

__all__ = ["sio", "emit", "emit_sync"]


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        else:
            return super().default(o)


json.JSONEncoder = JSONEncoder

REDIS_URL = os.environ.get("REFLECTEE_REDIS_URL", None)
if REDIS_URL:
    mgr: socketio.AsyncRedisManager = socketio.AsyncRedisManager(REDIS_URL)
else:
    mgr = None

sio: socketio.AsyncServer = socketio.AsyncServer(
    # aiohttp
    # asgi
    async_mode="asgi",
    client_manager=mgr,
    cors_allowed_origins="*",
    # engineio_logger=False,
    # logger=settings.DEBUG,
)

sessions = {}


@sio.event
# async def connect(sid, environ, auth):
async def connect(sid, environ, auth):

    sessions[sid] = Session(sio, sid, environ, auth)


@sio.event
async def disconnect(sid):
    # async def disconnect(sid):
    await sessions[sid].close()
    del sessions[sid]


@sio.on("*")
async def catch_all(event, sid, data):
    return await sessions[sid].on(event, data)


async def emit(*args, **kwargs):
    await sio.emit(*args, **kwargs)


def emit_sync(*args, **kwargs):
    async_to_sync(sio.emit)(*args, **kwargs)


# @sio.on('connection-bind')
# async def connection_bind(sid, data):
#                // code to capture the data
#    // sid is a unique id for each connection and data contains additional payload of the message.

# @sio.on('disconnect')
# async def test_disconnect(sid):
#     // code to capture the data
#    // sid is a unique id for each connection and data contains additional payload of the message.
