import sys
import json
import logging
import os
import tempfile
import threading
import codecs
import traceback
import time

from enum import Enum
from dust import Datatypes, ValueTypes, Operation, MetaProps, FieldProps
from dust.entity import Store, Entity, get_unit_deps_tuple

PATH = "/var/local/beaconing/messagequeue"

UNIT_MESSAGES = "messages"
UNIT_MESSAGES_META = "messages_meta"
UNIT_ID = 5
UNIT_META_ID = 6

def get_unit_dependencies():
    return [
        get_unit_deps_tuple("dust.events", "UNIT_EVENTS", "EventTypes")
    ]

class MessageType(Enum):
    ENTITY_ACCESS = 0

class MessageMeta(MetaProps):
    message_type = (Datatypes.STRING, ValueTypes.SINGLE, 1, 100)
    message_params = (Datatypes.JSON, ValueTypes.MAP, 2, 101)
    datetime = (Datatypes.ENTITY, ValueTypes.SINGLE, 3, 102)
    entities = (Datatypes.ENTITY, ValueTypes.SET, 4, 103)
    callback_name = (Datatypes.STRING, ValueTypes.SINGLE, 1, 104)

class MessageQueueInfoMeta(MetaProps):
    chunksize = (Datatypes.INT, ValueTypes.SINGLE, 1, 200)
    size = (Datatypes.INT, ValueTypes.SINGLE, 2, 201)
    tail = (Datatypes.INT, ValueTypes.LIST, 3, 202)
    head = (Datatypes.INT, ValueTypes.LIST, 4, 203)

class MessageTypes(FieldProps):
    message = (UNIT_MESSAGES_META, MessageMeta, 1)
    message_queue_info = (UNIT_MESSAGES_META, MessageQueueInfoMeta, 2)

Store.create_unit(UNIT_MESSAGES, UNIT_ID)
Store.load_types_from_enum(MessageTypes, UNIT_META_ID)

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
_log.addHandler(handler)

class EmptyMessageQueue(Exception):
    pass

class FullMessageQueue(Exception):
    pass

def _truncate(fn, length):
    with open(fn, 'ab+') as f:
        f.truncate(length)

def atomic_rename(src, dst):
    try:
        os.replace(src, dst)
    except: 
        traceback.print_exc()

class EntityJsonSerializer():
    def dump(self, obj, fp):
        if isinstance(obj, Entity):
            fp.write(json.dumps(obj.to_json()).encode())
            fp.write(b"\n")
        elif isinstance(obj, list):
            objs = []
            for e in obj:
                if isinstance(e, Entity):
                    objs.append(e.to_json())
                else:
                    raise ValueError("Only entity object can be serialized!")
            fp.write(json.dumps(objs).encode())
            fp.write(b"\n")
        else:
            raise ValueError("Only entity object can be serialized!")

    def load(self, f):
        try:
            data = json.loads(f.readline().decode())
            if not isinstance(data, list):
                data = [data]
            return Store.from_json(data)
        except:
            raise ValueError("Invalid json data in messagequeue!")


class MessageQueue():
    def __init__(self, path, maxsize=0, chunksize=100, tempdir=None, serializer=EntityJsonSerializer(), autosave=False):
        """Create a persistent queue object on a given path.
        The argument path indicates a directory where enqueued data should be
        persisted. If the directory doesn't exist, one will be created.
        If maxsize is <= 0, the queue size is infinite. The optional argument
        chunksize indicates how many entries should exist in each chunk file on
        disk.
        The tempdir parameter indicates where temporary files should be stored.
        The tempdir has to be located on the same disk as the enqueued data in
        order to obtain atomic operations.

        The serializer parameter controls how enqueued data is serialized. It
        must have methods dump(value, fp) and load(fp). The dump method must
        serialize value and write it to fp, and may be called for multiple
        values with the same fp. The load method must deserialize and return
        one value from fp, and may be called multiple times with the same fp
        to read multiple values.

        The autosave parameter controls when data removed from the queue is
        persisted. By default (disabled), the change is only persisted when
        task_done() is called. If autosave is enabled, data is persisted
        immediately when get() is called. Adding data to the queue with put()
        will always persist immediately regardless of this setting.
        """
        _log.debug('Initializing File based Queue with path {}'.format(path))
        self.path = path
        self.chunksize = chunksize
        self.tempdir = tempdir
        self.maxsize = maxsize
        self.serializer = serializer
        self.autosave = autosave
        self._init(maxsize)
        if self.tempdir:
            if os.stat(self.path).st_dev != os.stat(self.tempdir).st_dev:
                raise ValueError("tempdir has to be located on same path filesystem")
        else:
            fd, tempdir = tempfile.mkstemp()
            if os.stat(self.path).st_dev != os.stat(tempdir).st_dev:
                self.tempdir = self.path
                _log.warning("Default tempdir '%(dft_dir)s' is not on the " +
                            "same filesystem with queue path '%(queue_path)s'" +
                            ",defaulting to '%(new_path)s'." % {
                                "dft_dir": tempdir,
                                "queue_path": self.path,
                                "new_path": self.tempdir})
            os.close(fd)
            os.remove(tempdir)

        self.info = self._loadinfo()
        # truncate head case it contains garbage
        hnum, hcnt, hoffset = self.info.access(Operation.GET, [0, 0, 0], MessageQueueInfoMeta.head)
        headfn = self._qfile(hnum)
        if os.path.exists(headfn):
            if hoffset < os.path.getsize(headfn):
                _truncate(headfn, hoffset)
        # let the head file open
        self.headf = self._openchunk(hnum, 'ab+')
        # let the tail file open
        tnum, _, toffset = self.info.access(Operation.GET, [0, 0, 0], MessageQueueInfoMeta.tail)
        self.tailf = self._openchunk(tnum)
        self.tailf.seek(toffset)
        # update unfinished tasks with the current number of enqueued tasks
        self.unfinished_tasks = self.info.access(Operation.GET, 0, MessageQueueInfoMeta.size)
        # optimize info file updates
        self.update_info = True

    def _init(self, maxsize):
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def join(self):
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()

    def qsize(self):
        n = None
        with self.mutex:
            n = self._qsize()
        return n

    def _qsize(self):
        return self.info.access(Operation.GET, None, MessageQueueInfoMeta.size)

    def empty(self):
        return self.qsize() == 0

    def put(self, item, block=True, timeout=None):
        "Interface for putting item in disk-based queue."
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise FullMessageQueue
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0:
                            raise FullMessageQueue
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def _put(self, item):
        self.serializer.dump(item, self.headf)
        self.headf.flush()
        print(str(self.info.access(Operation.GET, None, MessageQueueInfoMeta.head)))
        hnum, hpos, _ = self.info.access(Operation.GET, None, MessageQueueInfoMeta.head)
        hpos += 1
        if hpos == self.info.access(Operation.GET, None, MessageQueueInfoMeta.chunksize):
            hpos = 0
            hnum += 1
            # make sure data is written to disk whatever
            # its underlying file system
            os.fsync(self.headf.fileno())
            self.headf.close()
            self.headf = self._openchunk(hnum, 'ab+')
        self.info.access(Operation.CHANGE, 1, MessageQueueInfoMeta.size)
        self.info.access(Operation.SET, [hnum, hpos, self.headf.tell()], MessageQueueInfoMeta.head)
        self._saveinfo()

    def put_nowait(self, item):
        return self.put(item, False)

    def get(self, block=True, timeout=None):
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise EmptyMessageQueue
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise EmptyMessageQueue
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item
        finally:
            self.not_empty.release()

    def get_nowait(self):
        return self.get(False)

    def _get(self):
        tnum, tcnt, toffset = self.info.access(Operation.GET, None, MessageQueueInfoMeta.tail)
        hnum, hcnt, _ = self.info.access(Operation.GET, None, MessageQueueInfoMeta.head)
        if [tnum, tcnt] >= [hnum, hcnt]:
            return None
        data = self.serializer.load(self.tailf)
        toffset = self.tailf.tell()
        tcnt += 1
        if tcnt == self.info.access(Operation.GET, None, MessageQueueInfoMeta.chunksize) and tnum <= hnum:
            tcnt = toffset = 0
            tnum += 1
            self.tailf.close()
            self.tailf = self._openchunk(tnum)
        self.info.access(Operation.CHANGE, -1, MessageQueueInfoMeta.size)
        self.info.access(Operation.SET, [tnum, tcnt, toffset], MessageQueueInfoMeta.tail)
        if self.autosave:
            self._saveinfo()
            self.update_info = False
        else:
            self.update_info = True
        return data

    def task_done(self):
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError("task_done() called too many times.")
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
            self._task_done()

    def _task_done(self):
        if self.autosave:
            return
        if self.update_info:
            self._saveinfo()
            self.update_info = False

    def _openchunk(self, number, mode='rb'):
        return open(self._qfile(number), mode)

    def _loadinfo(self):
        infopath = self._infopath()
        if os.path.exists(infopath):
            with open(infopath, 'rb') as f:
                info = self.serializer.load(f)
                return info[0]
        else:
            info = Store.access(Operation.GET, None, UNIT_MESSAGES, 1, MessageTypes.message_queue_info)
            info.access(Operation.SET, self.chunksize, MessageQueueInfoMeta.chunksize)
            info.access(Operation.SET, 0, MessageQueueInfoMeta.size)
            info.access(Operation.SET, [0, 0, 0], MessageQueueInfoMeta.tail)
            info.access(Operation.SET, [0, 0, 0], MessageQueueInfoMeta.head)

            print("INfo is {}".format(info.access(Operation.GET, None, MessageQueueInfoMeta.head)))

        return info

    def _gettempfile(self):
        if self.tempdir:
            return tempfile.mkstemp(dir=self.tempdir)
        else:
            return tempfile.mkstemp()

    def _saveinfo(self):
        tmpfd, tmpfn = self._gettempfile()
        with os.fdopen(tmpfd, "wb") as tmpfo:
            self.serializer.dump(self.info, tmpfo)
        atomic_rename(tmpfn, self._infopath())
        self._clear_tail_file()

    def _clear_tail_file(self):
        """Remove the tail files whose items were already get."""
        tnum, _, _ = self.info.access(Operation.GET, None, MessageQueueInfoMeta.tail)
        while tnum >= 1:
            tnum -= 1
            path = self._qfile(tnum)
            if os.path.exists(path):
                os.remove(path)
            else:
                break

    def _qfile(self, number):
        return os.path.join(self.path, 'q%05d' % number)

    def _infopath(self):
        return os.path.join(self.path, 'info')

    def __del__(self):
        """Handles the removal of queue."""
        for to_close in [self.headf, self.tailf]:
            if to_close and not to_close.closed:
                to_close.close() 

def register_listener(name, entity_filter, cb):
    _listeners[name] = (entity_filter, cb)


def unregister_listener(name):
    if name in _listeners:
        del _listeners[name]

_stop = False
_queue = MessageQueue(PATH)
_listeners = {}

def signal_finish():
    global _stop

    _stop = True
    _queue.put(Store.access(Operation.GET, None, UNIT_MESSAGES, None, MessageTypes.message))

def start_queue_processor(queue, log):
    global _stop

    while True:
        try:
            item = _queue.get()
            if item == None:
                time.sleep(0.5)
            else:
                _log.debug("Processing item: {}".format([i.global_id() for i in item]))
                for entity in item:
                    try:
                        _listeners[entity.access(Operation.GET, None, MessageMeta.callback_name)][1](
                            entity.access(Operation.GET, None, MessageMeta.message_type),
                            entity.access(Operation.GET, None, MessageMeta.message_params),
                            entity.access(Operation.GET, None, MessageMeta.entities)
                        )
                    except KeyError:
                        if entity.access(Operation.GET, None, MessageMeta.callback_name):
                            _log.error("Invalid callback registered: {}".format(entity.access(Operation.GET, None, MessageMeta.callback_name)))
            if _stop:
                break

        except EmptyMessageQueue:
            time.sleep(0.5)
            if _stop:
                break
        except KeyboardInterrupt:
            _log.warning("Keyboard interrupt received")
            break
        except:
            traceback.print_exc()

def create_message(message_type, message_params, entities):
    for callback_name, listener in _listeners.items():
        entity_filter, cb = listener
        if entity_filter(message_type, message_params, entities):
            message = Store.access(Operation.GET, None, UNIT_MESSAGES, None, MessageTypes.message)
            message.access(Operation.SET, message_type.name, MessageMeta.message_type)
            message.access(Operation.SET, callback_name, MessageMeta.callback_name)
            if message_params:
                message.access(Operation.SET, message_params, MessageMeta.message_params)
            if entities:
                for e in entities:
                    if e:
                        message.access(Operation.ADD, entities, MessageMeta.entities)
            _queue.put(message)


_queue_processor = threading.Thread(target=start_queue_processor, args=(_queue, _log, ), daemon=False)
_queue_processor.start()