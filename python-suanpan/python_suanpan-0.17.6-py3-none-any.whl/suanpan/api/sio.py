# coding=utf-8
from __future__ import absolute_import, print_function

import socketio
from suanpan.api import auth


def sio(*args, **kwargs):
    kwargs["headers"] = {**auth.defaultHeaders(), **kwargs.pop("headers", {})}
    client = socketio.Client()
    client.connect(*args, **kwargs)

    return client
