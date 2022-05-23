import os
import django
import socketio
from django.core.asgi import get_asgi_application
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


django.setup()
from django.conf import settings
os.environ.setdefault("REFLECTEE_REDIS_URL", getattr(settings, 'REFLECTEE_REDIS_URL', None))

from ..server import sio
app: socketio.ASGIApp = socketio.ASGIApp(sio, get_asgi_application())