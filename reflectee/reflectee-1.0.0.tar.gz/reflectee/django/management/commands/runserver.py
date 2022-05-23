import os

# import daphne
from django.core.management.commands.runserver import Command as RunCommand

ASYNC_SERVER = bool(int(os.environ.get("ASYNC_SERVER", "1")))


class Command(RunCommand):
    help = "Run the Socket.IO server"

    def handle(self, *args, **options):

        from reflectee.django.asgi import app, sio

        if sio.async_mode == "asgi":
            super(Command, self).handle(*args, **options)

        elif sio.async_mode == "daphne":
            # deploy with eventlet
            pass

        else:
            super(Command, self).handle(*args, **options)



        # from app.conf.server import app, sio

        # if sio.async_mode == "asgi":
        #     super(Command, self).handle(*args, **options)

        # elif sio.async_mode == "daphne":
        #     # deploy with eventlet
        #     pass

        # else:
        #     super(Command, self).handle(*args, **options)

        # else:

        #     if sio.async_mode == 'threading':
        #         super(Command, self).handle(*args, **options)

        #     elif sio.async_mode == 'eventlet':
        #         # deploy with eventlet
        #         import eventlet
        #         import eventlet.wsgi
        #         eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

        #     elif sio.async_mode == 'gevent':
        #         # deploy with gevent
        #         from gevent import pywsgi
        #         try:
        #             from geventwebsocket.handler import WebSocketHandler
        #             websocket = True
        #         except ImportError:
        #             websocket = False
        #         if websocket:
        #             pywsgi.WSGIServer(
        #                 ('', 8000), app,
        #                 handler_class=WebSocketHandler).serve_forever()
        #         else:
        #             pywsgi.WSGIServer(('', 8000), app).serve_forever()

        #     elif sio.async_mode == 'gevent_uwsgi':
        #         print('Start the application through the uwsgi server. Example:')
        #         print('uwsgi --http :5000 --gevent 1000 --http-websockets '
        #             '--master --wsgi-file django_example/wsgi.py --callable '
        #             'application')
        #     else:
        #         print('Unknown async_mode: ' + sio.async_mode)
