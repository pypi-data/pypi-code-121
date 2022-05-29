from veet.core.logging import Log
from ..application import Application
from importlib import import_module

app = Application()
app.bootstrap()

try:
    server = import_module(f"server")
except Exception as exception:
    if type(exception).__name__ != "ModuleNotFoundError":
        Log.error(f"server.py :: {exception}")
    server = None


@app.on_event("startup")
async def on_startup():
    try:
        await getattr(server, 'on_startup')(app)
    except Exception as exception:
        if type(exception).__name__ != "AttributeError":
            Log.error(f"Event Startup :: {exception}")


@app.on_event("shutdown")
async def on_shutdown():
    try:
        await getattr(server, 'on_shutdown')(app)
    except Exception as exception:
        if type(exception).__name__ != "AttributeError":
            Log.error(f"Event Shutdown :: {exception}")
