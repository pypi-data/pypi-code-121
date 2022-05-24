import socket
import threading
import time

from rook.com_ws.envelope_wrappers.basic_envelope_wrapper import BasicEnvelopeWrapper
from rook.com_ws.envelope_wrappers.basic_serialized_envelope_wrapper import BasicSerializedEnvelopeWrapper
from rook.com_ws.envelope_wrappers.protobuf_2_envelope_wrapper import Protobuf2EnvelopeWrapper
from six.moves.queue import Queue, Empty
from six.moves.urllib.parse import urlparse
import select
import errno
import certifi
import ssl
import re
import os
import six
import websocket

from rook.exceptions import RookCommunicationException, RookInvalidToken, RookDependencyConflict, RookQueueSizeExceeded, RookMissingToken
import rook.com_ws.socketpair_compat  # do not remove - adds socket.socketpair on Windows lgtm[py/unused-import]

try:
    from websocket import WebSocketBadStatusException # This is used to make sure we have the right version lgtm[py/unused-import]
except ImportError:
    raise RookDependencyConflict('websocket')

# Python < 2.7.9 is missing important SSL features for websocket
# (unless supplied by CentOS etc)
if not websocket._ssl_compat.HAVE_SSL:
    try:
        import backports.ssl
        import backports.ssl_match_hostname
        websocket._http.ssl = backports.ssl
        websocket._http.HAVE_SSL = True
        websocket._http.HAVE_CONTEXT_CHECK_HOSTNAME = True
    except ImportError:
        six.print_('[Rookout] Python is missing modern SSL features. To rectify, please run:\n'
                   '  pip install rook[ssl_backport]')

from rook.com_ws import information
from rook.logger import logger
import rook.protobuf.messages_pb2 as messages_pb
import rook.protobuf.envelope_pb2 as envelope_pb
from rook.config import AgentComConfiguration, VersionConfiguration


def wrap_in_envelope(message):
    envelope = envelope_pb.Envelope()
    envelope.timestamp.GetCurrentTime()
    envelope.msg.Pack(message)

    return envelope.SerializeToString()


class ExitThreadSentinel(object):
    pass


class FlushMessagesEvent(object):
    def __init__(self):
        self.event = threading.Event()


class MessageCallback(object):
    def __init__(self, cb, persistent):
        self.cb = cb
        self.persistent = persistent


class AgentCom(object):
    def __init__(self, agent_id, host, port, proxy, token, labels, tags, debug, print_on_initial_connection):
        self.id = agent_id

        self._init_connect_thread()

        self._host = host if '://' in host else 'ws://' + host
        self._port = port
        self._proxy = proxy
        self._token = token
        self._token_valid = False
        self._labels = labels or {}
        self._tags = tags or []

        self._loop = None
        self._connection = None

        # Queue hold outgoing messages wrapped with IEnvelopeWrapper
        self._queue = Queue()
        self._queue_messages_length = 0

        self._running = True

        self._ready_event = threading.Event()
        self._connection_error = None

        self.debug = debug

        self._callbacks = {}
        self._print_on_initial_connection = print_on_initial_connection

        def set_ready_event(*args):
            self._ready_event.set()

        self.once('InitialAugsCommand', set_ready_event)
        self.poll_available = hasattr(select, "poll")

    def start(self):
        self._thread.start()

    def stop(self):
        if not self._running:
            return

        self._running = False

        if self._connection is not None:
            self._connection.close(1000)

        self._thread.join()

        if self._connection is not None:
            self._connection.close(1000)
            self._connection = None

    def restart(self):
        self.stop()

        self._init_connect_thread()

        self._running = True
        self.start()

    def update_info(self, agent_id, tags, labels):
        self.id = agent_id
        self._labels = labels or {}
        self._tags = tags or []

    def send_user_message(self, aug_id, message_id, arguments):
        envelope = Protobuf2EnvelopeWrapper(self.id, aug_id, message_id, arguments)

        return self.add_envelope(envelope)

    def add(self, message):
        if self._queue.qsize() >= AgentComConfiguration.MAX_QUEUED_MESSAGES:
            return None

        envelope = BasicSerializedEnvelopeWrapper(message)
        return self.add_envelope(envelope)

    def add_envelope(self, envelope):
        if len(envelope) + self._queue_messages_length > AgentComConfiguration.MAX_QUEUE_MESSAGES_LENGTH:
            return RookQueueSizeExceeded(len(envelope), self._queue_messages_length, AgentComConfiguration.MAX_QUEUE_MESSAGES_LENGTH)

        self._queue_messages_length += len(envelope)
        self._queue.put(envelope)
        return None

    def is_queue_full(self):
        return self._queue.qsize() >= AgentComConfiguration.MAX_QUEUED_MESSAGES

    def on(self, message_name, callback):
        self._register_callback(message_name, MessageCallback(callback, True))

    def once(self, message_name, callback):
        self._register_callback(message_name, MessageCallback(callback, False))

    def await_message(self, message_name):
        event = threading.Event()
        self.once(message_name, lambda _: event.set())

        return event

    def wait_for_ready(self, timeout=None):
        if not self._ready_event.wait(timeout):
            raise RookCommunicationException()
        else:
            if self._connection_error is not None:
                raise self._connection_error

    def _connect(self):
        retry = 0
        backoff = AgentComConfiguration.BACK_OFF
        connected = False
        last_successful_connection = 0

        while self._running:
            try:
                try:
                    if connected and time.time() >= last_successful_connection + AgentComConfiguration.RESET_BACKOFF_TIMEOUT:
                        retry = 0
                        backoff = AgentComConfiguration.BACK_OFF

                    self._connection = self._create_connection()

                    self._register_agent(self.debug)

                except websocket.WebSocketBadStatusException as e:
                    if not self._token_valid and e.status_code == 403:# invalid token
                        if self._token is None:
                            self._connection_error = RookMissingToken()
                        else:
                            self._connection_error = RookInvalidToken(self._token)
                        self._ready_event.set()

                        logger.error('Connection failed; %s', self._connection_error.get_message())
                    raise
            except Exception as e:
                retry += 1
                backoff = min(backoff * 2, AgentComConfiguration.MAX_SLEEP)
                connected = False

                if hasattr(e, 'message') and e.message:
                    reason = e.message
                else:
                    reason = str(e)

                logger.info('Connection failed; reason = %s, retry = #%d, waiting %.3fs', reason, retry, backoff)

                time.sleep(backoff)
                continue
            else:
                connected = True
                last_successful_connection = time.time()

            if self._print_on_initial_connection:
                # So there is no print on reconnect
                self._print_on_initial_connection = False
                six.print_("[Rookout] Successfully connected to controller.")
            logger.debug("WebSocket connected successfully")
            self._token_valid = True

            stop_socket_incoming, incoming_client_socket = socket.socketpair()
            outgoing_exit_sentinel = ExitThreadSentinel()

            def signal_stop_incoming_thread():
                # Logging is not safe here, interpreter might be shutting down
                try:
                    stop_socket_incoming.send(b'1')
                except socket.error as socket_error:
                    if socket_error.errno == errno.EPIPE:
                        return

                    logger.debug("Failed to signal stop", exc_info=1)
                except Exception:
                    logger.debug("Failed to signal stop", exc_info=1)
                finally:
                    try:
                        stop_socket_incoming.close()
                    except:  # lgtm[py/catch-base-exception]
                        pass

            def signal_stop_outgoing_thread():
                # Logging is not safe here, interpreter might be shutting down
                try:
                    incoming_client_socket.close()
                except:  # Nothing to do as we are already closing
                    pass

                try:
                    self._queue.put(BasicEnvelopeWrapper(outgoing_exit_sentinel))
                except Exception:
                    logger.debug("Failed to signal stop", exc_info=1)

            routines = [threading.Thread(name="rookout-incoming-thread", target=self._incoming, args=(incoming_client_socket, signal_stop_outgoing_thread)),
                        threading.Thread(name="rookout-outgoing-thread", target=self._outgoing, args=(outgoing_exit_sentinel, signal_stop_incoming_thread))]

            for routine in routines:
                routine.daemon = True
                routine.start()

            logger.info("Finished initialization")

            for routine in routines:
                routine.join()

            logger.debug("Reconnecting")

    def wait_for_event_poll(self, stop_socket):
        poller = select.poll()

        exception_flags = select.POLLHUP | select.POLLERR
        read_only_flags = select.POLLIN | select.POLLPRI | exception_flags

        # Registering all input close and exception types
        poller.register(self._connection, read_only_flags)
        poller.register(stop_socket, read_only_flags)

        events = poller.poll(AgentComConfiguration.PING_TIMEOUT * 1000)

        try:
            for fd, flag in events:
                if fd == stop_socket.fileno():
                    return True  # signaled to stop
                elif fd == self._connection.fileno() and flag \
                        and flag & exception_flags:  # Checking these flags explicitly (ignore input data)
                    return True
        except AttributeError:  # happens when the socket is already None (and fileno() will fail)
            return True  # Should stop

        if len(events) == 0:
            logger.debug("Incoming thread - ping timeout")
            return True  # select timed out - ping timeout

        # Every thing is ok
        return False

    def wait_for_event_select(self, stop_socket):
        rlist, _, xlist = select.select([self._connection, stop_socket],
                                        [],
                                        [self._connection, stop_socket],
                                        AgentComConfiguration.PING_TIMEOUT)
        if stop_socket in rlist or stop_socket in xlist or self._connection in xlist:
            return True  # signaled to stop

        if len(rlist) == 0 and len(xlist) == 0:
            logger.debug("Incoming thread - ping timeout")
            return True  # select timed out - ping timeout
        return False

    def _incoming(self, stop_socket, on_exit):
        try:
            while self._running:
                try:
                    # Poll has no file_descriptor limit (on linux) if available - use it
                    if self.poll_available:
                        if self.wait_for_event_poll(stop_socket):
                            break
                    else:
                        if self.wait_for_event_select(stop_socket):
                            break

                    # it wasn't stop_socket, so it's self._connection -> we can read. we have to read including
                    # control frames, otherwise select might return and recv() wouldn't actually return anything
                    code, msg = self._connection.recv_data(control_frame=True)
                    if code != websocket.ABNF.OPCODE_BINARY:
                        continue

                    if msg is None:
                        # socket disconnected
                        logger.debug("Incoming thread - socket disconnected")
                        break

                    if len(msg) > AgentComConfiguration.AGENT_COM_INCOMING_MAX_MESSAGE_SIZE:
                        logger.error("message length (%d) exceed max size", msg)
                        continue

                    envelope = envelope_pb.Envelope()
                    envelope.ParseFromString(msg)
                    self._handle_incoming_message(envelope)
                except (socket.error, websocket.WebSocketConnectionClosedException):
                    logger.debug("Incoming thread - socket disconnected")
                    break
        except: # lgtm[py/catch-base-exception]
            try:
                logger.exception("Incoming thread failed")
            except:  # lgtm[py/catch-base-exception]
                pass
        finally:
            on_exit()

    def flush_all_messages(self):
        flush_event = FlushMessagesEvent()
        self._queue.put(BasicEnvelopeWrapper(flush_event))
        flush_event.event.wait(AgentComConfiguration.FLUSH_TIMEOUT)

    def _outgoing(self, outgoing_exit_sentinel, on_exit):
        try:
            last_ping = time.time()
            self._connection.ping()

            while self._running:
                envelope_wrapper = None
                if (time.time() - last_ping) >= AgentComConfiguration.PING_INTERVAL:
                    last_ping = time.time()
                    self._connection.ping()

                try:
                    envelope_wrapper = self._queue.get(timeout=AgentComConfiguration.PING_INTERVAL)
                    if envelope_wrapper is None:
                        break
                    msg = envelope_wrapper.get_buffer()
                    if isinstance(msg, ExitThreadSentinel):
                        if msg is outgoing_exit_sentinel:
                            break
                        continue  # if it's an ExitThreadSentinel but not from this specific thread, just skip it
                    if isinstance(msg, FlushMessagesEvent):
                        msg.event.set()
                        continue
                    self._send(msg)
                except Empty:
                    continue
                except (socket.error, websocket.WebSocketConnectionClosedException):
                    if envelope_wrapper is not None:
                        self._queue.put(envelope_wrapper)
                    break

                if envelope_wrapper is not None:
                    self._queue_messages_length -= len(envelope_wrapper)

        except:  # lgtm[py/catch-base-exception]
            try:
                logger.exception("Outgoing thread failed")
            except:  # lgtm[py/catch-base-exception]
                pass
        finally:
            on_exit()

    def _create_connection(self):
        url = '{}:{}/v1'.format(self._host, self._port)
        headers = {
            'User-Agent': 'RookoutAgent/{}+{}'.format(VersionConfiguration.VERSION, VersionConfiguration.COMMIT)
        }

        if self._token is not None:
            headers["X-Rookout-Token"] = self._token

        proxy_host, proxy_port = self._get_proxy()

        connect_args = (url,)
        connect_kwargs = dict(header=headers,
                              timeout=AgentComConfiguration.TIMEOUT,
                              http_proxy_host=proxy_host,
                              http_proxy_port=proxy_port,
                              enable_multithread=True)

        if os.environ.get('ROOKOUT_NO_HOST_HEADER_PORT') == '1':
            host = re.sub(':\d+$', '', urlparse(url).netloc)
        else:
            host = None
        
        connect_kwargs['sslopt'] = dict()

        if os.environ.get('ROOKOUT_SKIP_SSL_VERIFY') == '1':
            connect_kwargs['sslopt']['cert_reqs']=ssl.CERT_NONE

        try:
            # connect using system certificates
            conn = websocket.create_connection(*connect_args, host=host, **connect_kwargs)
        # In some very specific scenario, you cannot
        # reference ssl.CertificateError because it does
        # exist, so instead we get with with getattr
        # (None never matches an exception)
        except (ssl.SSLError, getattr(ssl, 'CertificateError', None)):
            # connect using certifi certificate bundle
            # (Python 2.7.15+ from python.org on macOS rejects our CA, see RK-3383)
            connect_kwargs['sslopt']['ca_certs']=certifi.where()
            logger.debug("Got SSL error when connecting using system CA cert store, falling back to certifi")
            conn = websocket.create_connection(*connect_args, **connect_kwargs)
        conn.settimeout(None)
        return conn

    def _get_proxy(self):
        if self._proxy is None:
            return None, None

        try:
            if not self._proxy.startswith("http://"):
                self._proxy = "http://" + self._proxy

            url = urlparse(self._proxy, "http://")

            logger.debug("Connecting via proxy: %s", url.netloc)

            return url.hostname, url.port
        except ValueError:
            return None, None

    def _register_agent(self, debug):
        logger.info('Registering agent with id %s', self.id)
        info = information.collect(debug)
        info.agent_id = self.id
        info.labels = self._labels
        info.tags = self._tags

        m = messages_pb.NewAgentMessage()
        m.agent_info.CopyFrom(information.pack_agent_info(info))

        return self._send(wrap_in_envelope(m))

    def _init_connect_thread(self):
        self._thread = threading.Thread(name="rookout-" + type(self).__name__, target=self._connect)
        self._thread.daemon = True

    AcceptedMessageTypes = [
        messages_pb.InitialAugsCommand,
        messages_pb.AddAugCommand,
        messages_pb.ClearAugsCommand,
        messages_pb.PingMessage,
        messages_pb.RemoveAugCommand
    ]

    def _handle_incoming_message(self, envelope):
        for message_type in self.AcceptedMessageTypes:
            if envelope.msg.Is(message_type.DESCRIPTOR):
                message = message_type()
                envelope.msg.Unpack(message)
                type_name = message.DESCRIPTOR.name

                callbacks = self._callbacks.get(type_name)

                if callbacks:
                    persistent_callbacks = []

                    # Trigger all persistent callbacks first
                    for callback in callbacks:
                        try:
                            if callback.persistent:
                                callback.cb(message)
                        except Exception:  # We ignore errors here, they are high unlikely and the code is too deep
                            pass
                        finally:
                            if callback.persistent:
                                persistent_callbacks.append(callback)

                    # Trigger all non persistent callbacks
                    for callback in callbacks:
                        try:
                            if not callback.persistent:
                                callback.cb(message)
                        except Exception:  # We ignore errors here, they are high unlikely and the code is too deep
                            pass

                    self._callbacks[type_name] = persistent_callbacks

    def _send(self, message):
        return self._connection.send_binary(message)

    def _register_callback(self, message_name, callback):
        self._callbacks.setdefault(message_name, []).append(callback)
