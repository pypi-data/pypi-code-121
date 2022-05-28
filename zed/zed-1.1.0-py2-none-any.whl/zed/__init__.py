"""
zed is Twisted zmq (twist the second and third glyphs of zmq around a bit and
you wind up with zed. Get it? Ha! I kill me.... :)

This module is based on an old version of txZMQ but uses a much lighter-weight
interface. Whereas txZMQ strives to conform to Twisted's norms, this
implementation provides only the bare minimum needed to hook pyzmq sockets into
the Twisted reactor.
"""

from collections import deque

from zmq import constants, error
from zmq import Socket
from zmq import Context
from zmq import PUB, SUB, REQ, REP, PUSH, PULL, ROUTER, DEALER, PAIR

from zope.interface import implementer

from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor
from twisted.internet import reactor
from twisted.python   import log


_context = None # ZmqContext singleton


POLL_IN_OUT = constants.POLLOUT & constants.POLLIN


def getContext():
    if _context is not None:
        return _context
    else:
        return _ZmqContext()

def _cleanup():
    global _context
    if _context:
        _context.shutdown()
    

class _ZmqContext(object):
    """
    This class wraps a ZeroMQ Context object and integrates it into the
    Twisted reactor framework.
    """

    reactor = reactor

    def __init__(self, io_threads=1):
        """
        @param io_threads; Passed through to zmq.core.context.Context
        """
        global _context

        assert _context is None, 'Only one ZmqContext instance is permitted'
        
        self._sockets = set()
        self._zctx    = Context(io_threads)

        _context = self

        reactor.addSystemEventTrigger('during', 'shutdown', _cleanup)

    def shutdown(self):
        """
        Shutdown the ZeroMQ context and all associated sockets.
        """
        global _context

        if self._zctx is not None:
        
            for socket in self._sockets.copy():
                socket.close()

            self._sockets = None

            self._zctx.term()
            self._zctx = None

        _context = None
        

@implementer(IFileDescriptor)
@implementer(IReadDescriptor)
class ZmqSocket(object):
    """
    Wraps a ZeroMQ socket and integrates it into the Twisted reactor

    """
    #implements(IReadDescriptor, IFileDescriptor)

    socketType = None
    
    def __init__(self, socketType=None):
        """
        @param socketType: Type of socket to create. PUB, SUB, PUSH, etc.
        """
        if socketType is not None:
            self.socketType = socketType
            
        assert self.socketType is not None
        
        self._ctx   = getContext()
        self._zsock = Socket(getContext()._zctx, self.socketType)
        self._queue = deque()

        self.fd     = self._zsock.getsockopt(constants.FD)
        
        self._ctx._sockets.add(self)

        self._ctx.reactor.addReader(self)

        self.read_scheduled = None

        
    def _sockopt_property( i, totype=int):
        if totype is str:
            fget = lambda zs:   zs._zsock.getsockopt_string(i)
            fset = lambda zs,v: zs._zsock.setsockopt_string(i,totype(v))
        else:
            fget = lambda zs:   zs._zsock.getsockopt(i)
            fset = lambda zs,v: zs._zsock.setsockopt(i,totype(v))
        return property( fget, fset )

    
    linger     = _sockopt_property( constants.LINGER         )
    rate       = _sockopt_property( constants.RATE           )
    identity   = _sockopt_property( constants.IDENTITY,  str )
    subscribe  = _sockopt_property( constants.SUBSCRIBE, str )


    def close(self):
        self._ctx.reactor.removeReader(self)

        self._ctx._sockets.discard(self)

        self._zsock.close()
        
        self._zsock = None
        self._ctx   = None

        if self.read_scheduled is not None:
            self.read_scheduled.cancel()
            self.read_scheduled = None


    def __repr__(self):
        t = _type_map[ self.socketType ].lower()
        t = t[0].upper() + t[1:]
        return "Zmq%sSocket(%s)" % (t, repr(self._zsock))


    def logPrefix(self):
        """
        Part of L{ILoggingContext}.

        @return: Prefix used during log formatting to indicate context.
        @rtype: C{str}
        """
        return 'ZMQ'


    def fileno(self):
        """
        Part of L{IFileDescriptor}.

        @return: The platform-specified representation of a file descriptor
                 number.
        """
        return self.fd

    
    def connectionLost(self, reason):
        """
        Called when the connection was lost. This will only be called during
        reactor shutdown with active ZeroMQ sockets.

        Part of L{IFileDescriptor}.

        """
        if self._ctx:
            self._ctx.reactor.removeReader(self)

    
    def doRead(self):
        """
        Some data is available for reading on your descriptor.

        ZeroMQ is signalling that we should process some events,
        we're starting to send queued messages and to receive
        incoming messages.

        Note that the ZeroMQ FD is used in an edge-triggered manner.
        Consequently, this function must read all pending messages
        before returning.

        Part of L{IReadDescriptor}.
        """
        if self.read_scheduled is not None:
            if not self.read_scheduled.called:
                self.read_scheduled.cancel()
            self.read_scheduled = None
        
        while self._zsock is not None and self._ctx is not None:

            events = self._zsock.get(constants.EVENTS)

            if (events & constants.POLLIN) != constants.POLLIN:
                return
            
            try:
                msg_list = self._zsock.recv_multipart( constants.NOBLOCK )
            except error.ZMQError as e:
                if e.errno == constants.EAGAIN:
                    continue
                
                raise e
            
            # PY3: With Python2 version of pyzmq, `recv_multipart` returned list of strings.
            # However, with Python3 update of pyzmq, `recv_multipart` now returns list of raw bytes.
            # To maintain compatibility, we decode incoming bytes and return list of strings to
            # the client as before.
            msg_list = [m.decode() if isinstance(m, bytes) else m for m in msg_list]
            log.callWithLogger(self, self.messageReceived, msg_list)
                

            
    
    def send(self, *message_parts):
        """
        Sends a ZeroMQ message. Each positional argument is converted into a message part
        """
        if len(message_parts) == 1 and isinstance(message_parts[0], (list, tuple)):
            message_parts = message_parts[0]

        # Queue a read since touching the socket with a send sometimes causes zmq to
        # omit triggering a read
        if self.read_scheduled is None:
            self.read_scheduled = reactor.callLater(0, self.doRead)

        # PY3: With Python2 version of pyzmq, `send_multipart` accepted a list of str or bytes
        # and didn't have any specific distinction between the two.
        # However, with Python3 update of pyzmq, `send_multipart` accepts only list of raw bytes.
        # To maintain compatibility, we encode incoming strings to bytes and send it to the receiver.
        message_parts = [m.encode() if isinstance(m, str) else m for m in message_parts]
        self._zsock.send_multipart( message_parts, constants.NOBLOCK )


    def connect(self, addr):
        return self._zsock.connect(addr)

    
    def bind(self, addr):
        return self._zsock.bind(addr)

    
    def bindToRandomPort(self, addr, min_port=49152, max_port=65536, max_tries=100):
        return self._zsock.bind_to_random_port(addr, min_port, max_port, max_tries)

    
    def messageReceived(self, message_parts):
        """
        Called on incoming message from ZeroMQ.

        @param message_parts: list of message parts
        """
        raise NotImplementedError(self)


_type_map = dict( PUB    = PUB,
                  SUB    = SUB,
                  REQ    = REQ,
                  REP    = REP,
                  PUSH   = PUSH,
                  PULL   = PULL,
                  ROUTER = ROUTER,
                  DEALER = DEALER,
                  PAIR   = PAIR )

for k,v in list(_type_map.items()):
    _type_map[v] = k

class ZmqPubSocket(ZmqSocket):
    socketType = PUB
    def messageReceived(self, message_parts):
        pass

class ZmqSubSocket(ZmqSocket):
    socketType = SUB

class ZmqReqSocket(ZmqSocket):
    socketType = REQ

class ZmqRepSocket(ZmqSocket):
    socketType = REP

class ZmqPushSocket(ZmqSocket):
    socketType = PUSH
    def messageReceived(self, message_parts):
        pass

class ZmqPullSocket(ZmqSocket):
    socketType = PULL

class ZmqRouterSocket(ZmqSocket):
    socketType = ROUTER

class ZmqDealerSocket(ZmqSocket):
    socketType = DEALER

class ZmqPairSocket(ZmqSocket):
    socketType = PAIR
