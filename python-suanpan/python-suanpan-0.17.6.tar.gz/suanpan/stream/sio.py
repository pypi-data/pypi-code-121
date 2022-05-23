# coding=utf-8
from __future__ import absolute_import, print_function

import datetime
import io
import traceback
import urllib
import uuid

import geventwebsocket.handler

from suanpan import path, runtime
from suanpan.log import logger
from suanpan.stream import handlers
from suanpan.stream.interfaces import HasHandlers


class Event(object):
    TEMPLATE = "__{keyword}_::{event}::{data}__"

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._kwargs.setdefault("keyword", "akuma")

    def __call__(self, event, *args, **kwargs):
        kwargs.update(event=event)
        return self.format(*args, **kwargs)

    def format(self, *args, **kwargs):
        return self.TEMPLATE.format(*self._args, *args, **self._kwargs, **kwargs)

    def new(self):
        return self.format(event="new", data="id")

    def resume(self, id=""):
        return self.format(event="resume", data=id)

    def data(self, id):
        return self.format(event="data", data=id)

    def more(self, id):
        return self.format(event="more", data=id)

    def stop(self):
        return self.format(event="stop", data="")

    def end(self, id):
        return self.format(event="end", data=id)


class Stream(object):
    def __init__(self, id):
        self.record = {
            "id": id,
            "event": None,
            "size": 0,
            "total": 0,
            "expire": self._addExipre(new=True),
            "data": {},
        }
        self.buffer = io.BytesIO()

    def _addExipre(self, expire=None, new=False):
        expire = expire or self.now
        if new:
            return expire + datetime.timedelta(minutes=5)
        if (self.now - expire).seconds <= 60:
            return expire + datetime.timedelta(milliseconds=60)
        return expire

    @property
    def now(self):
        return datetime.datetime.now()

    @property
    def sid(self):
        return self.record["sid"]

    @property
    def event(self):
        return self.record["event"]

    @property
    def size(self):
        return self.record["size"]

    @property
    def total(self):
        return self.record["total"]

    @property
    def dirty(self):
        return self.record["dirty"]

    @property
    def expire(self):
        return self.record["expire"]

    @property
    def data(self):
        return self.record["data"]

    @property
    def expired(self):
        return self.now > self.expire

    @property
    def done(self):
        return self.total >= self.size

    def update(self, *args, **kwargs):
        self.record.update(*args, **kwargs)
        return self

    def read(self):
        self.buffer.seek(0)
        data = self.buffer.read()
        self.buffer.truncate(0)
        self.buffer.seek(0)
        return data

    def write(self, chunks):
        if not chunks:
            return 0

        total = self.buffer.write(chunks)
        self.update(total=self.total + total, expire=self._addExipre(self.expire))
        return total

    def pipe(self, file):
        path.mkdirs(file, parent=True)
        chunks = self.read()
        if self.total - len(chunks) <= 0:
            path.remove(file)
        with open(file, "ab") as f:
            return f.write(chunks)


class Cleaner(object):
    def __init__(self, delta, handler):
        self.delta = delta
        self.handler = handler
        self.expire = self.now + delta

    @property
    def now(self):
        return datetime.datetime.now()

    @property
    def expired(self):
        return self.now > self.expire

    def clean(self, *args, **kwargs):
        if self.expired:
            self.handler(*args, **kwargs)


class StreamServer(HasHandlers):
    DEFAULT_HANDLER_CLASS = handlers.SIOStreamHandler

    def __init__(self, stream, sio):
        super().__init__()
        self.stream = stream
        self.sio = sio
        self.streams = {}
        self.event = Event()
        self.cleaner = Cleaner(datetime.timedelta(seconds=10), self._clean)
        self.init()

    def init(self):
        self.sio.on(self.event.new(), self.onNew)
        self.sio.on(self.event.resume(), self.onResume)

    @property
    def now(self):
        return datetime.datetime.now()

    def _addTime(self, date, new=False):
        if new:
            return date + datetime.timedelta(minutes=5)
        if (self.now - date).seconds <= 60:
            return date + datetime.timedelta(milliseconds=60)
        return date

    def _genid(self):
        id = uuid.uuid4().hex
        while id in self.streams:
            id = uuid.uuid4().hex
        return id

    def _createNew(self, id):
        self._listener(id)
        return id

    def _listener(self, id):
        self.sio.on(self.event.data(id), lambda sid, data: self.onData(sid, id, data))

    def _done(self, id, *args, **kwargs):
        self.end(id, *args, **kwargs)
        self.streams.pop(id)

    def _clean(self):
        expireids = [id for id, stream in self.streams.items() if stream.expired]
        for id in expireids:
            self.streams.pop(id)

    def _handle(self, key, handler):
        def _dec(sid, data, stream):
            title = f"{sid} - sio:{key}"
            _run = runtime.costrun(title)(handler.run)
            try:
                return _run(self.stream, data, sid, stream)
            except Exception:  # pylint: disable=broad-except
                logger.error(traceback.format_exc())
                return None

        return _dec

    def getHandler(self, key):
        if not self.hasHandler(key):
            super().setHandler(key, self.DEFAULT_HANDLER_CLASS())
        return super().getHandler(key)

    def setHandler(self, key, handler):
        return self.getHandler(key).use(handler)

    def clean(self, *args, **kwargs):
        self.cleaner.clean(*args, **kwargs)

    def onNew(self, sid):  # pylint: disable=unused-argument
        return self._createNew(self._genid())

    def onData(self, sid, id, data):
        self.clean()

        stream = self.streams.get(id)
        if not stream:
            stream = Stream(id).update(event=data["event"], **data["info"])
            self.streams[id] = stream
        stream.write(data["chunk"])

        payload = None
        if self.hasHandler(stream.event):
            payload = self._handle(stream.event, self.getHandler(stream.event))(
                sid, stream.data, stream
            )

        if stream.done:
            self._done(id, {"total": stream.total, "payload": payload})
        else:
            self.more(id, stream.total)

    def onStop(self, sid, id):  # pylint: disable=unused-argument
        if id in self.streams:
            self._done(id)

    def onResume(self, sid, id):  # pylint: disable=unused-argument
        stream = self.streams.get(id)
        if stream:
            self.resume(id, stream.total)
        else:
            self._createNew(id)
            self.resume(id)

    def more(self, id, *args, **kwargs):
        self.sio.emit(self.event.more(id), *args, **kwargs)

    def resume(self, id, *args, **kwargs):
        self.sio.emit(self.event.resume(id), *args, **kwargs)

    def end(self, id, *args, **kwargs):
        self.sio.emit(self.event.end(id), *args, **kwargs)


class WebSocketHandler(geventwebsocket.handler.WebSocketHandler):
    def get_environ(self):
        env = super().get_environ()
        urlpath = self.path.split("?", 1)[0] if "?" in self.path else self.path
        env["PATH_INFO"] = urllib.parse.unquote(urlpath)
        return env
