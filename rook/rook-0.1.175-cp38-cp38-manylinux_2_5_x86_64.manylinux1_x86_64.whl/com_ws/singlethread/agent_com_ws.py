import threading
import time

from rook.com_ws.envelope_wrappers.basic_envelope_wrapper import BasicEnvelopeWrapper
from rook.com_ws.envelope_wrappers.basic_serialized_envelope_wrapper import BasicSerializedEnvelopeWrapper
from six.moves.urllib.parse import urlparse
import certifi
import ssl
import re
import os
import six
import websocket
import socket

from rook.com_ws.flush_messages_event import FlushMessagesEvent
from rook.exceptions import RookCommunicationException, RookInvalidToken, RookDependencyConflict, \
    RookMissingToken, RookQueueSizeExceeded
from rook.com_ws.envelope_wrappers.protobuf_2_envelope_wrapper import Protobuf2EnvelopeWrapper
from six.moves.queue import Empty

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

from rook.com_ws import information, selectable_event, selectable_queue, poll_select
from rook.logger import logger
import rook.protobuf.messages_pb2 as messages_pb
import rook.protobuf.envelope_pb2 as envelope_pb
from rook.config import AgentComConfiguration, VersionConfiguration


def wrap_in_envelope(message):
    envelope = envelope_pb.Envelope()
    envelope.timestamp.GetCurrentTime()
    envelope.msg.Pack(message)

    return envelope.SerializeToString()


class MessageCallback(object):
    def __init__(self, cb, persistent):
        self.cb = cb
        self.persistent = persistent


class AgentCom(object):
    def __init__(self, agent_id, host, port, proxy, token, labels, tags, debug, print_on_initial_connection):
        self.id = agent_id

        self._host = host if '://' in host else 'ws://' + host
        self._port = port
        self._proxy = proxy
        self._token = token
        self._token_valid = False
        self._labels = labels or {}
        self._tags = tags or []

        self._connection = None
        # Queue hold outgoing messages wrapped with IEnvelopeWrapper
        self._queue = selectable_queue.SelectableQueue()
        self._queue.messages_length = 0

        self._running = True

        self._ready_event = threading.Event()
        self._connection_error = None

        self.debug = debug

        self._callbacks = {}

        self._thread = None
        self._print_on_initial_connection = print_on_initial_connection

        def set_ready_event(*args):
            self._ready_event.set()

        self.once('InitialAugsCommand', set_ready_event)

    def start(self):
        self._init_connect_thread()
        self._thread.start()

    def stop(self):
        self._running = False

        if self._connection is not None:
            self._connection.close()

        if self._thread is not None:
            self._thread.join()
            self._thread = None

        if self._connection is not None:
            self._connection.close(1000)
            self._connection = None

    def restart(self):
        self.stop()

        self._connection = None

        logger.debug("set running to True (due to restart)")
        self._running = True
        self.start()

    def update_info(self, agent_id, tags, labels):
        self.id = agent_id
        self._labels = labels or {}
        self._tags = tags or []

    def send_user_message(self, aug_id, message_id, arguments):
        envelope = Protobuf2EnvelopeWrapper(self.id, aug_id, message_id, arguments)

        self.add_envelope(envelope)

    def add(self, message):
        if self._queue.qsize() >= AgentComConfiguration.MAX_QUEUED_MESSAGES:
            return None

        envelope = BasicSerializedEnvelopeWrapper(message)
        return self.add_envelope(envelope)

    def add_envelope(self, envelope):
        if len(envelope) + self._queue.messages_length > AgentComConfiguration.MAX_QUEUE_MESSAGES_LENGTH:
            return RookQueueSizeExceeded(len(envelope), self._queue.messages_length,
                                         AgentComConfiguration.MAX_QUEUE_MESSAGES_LENGTH)

        self._queue.messages_length += len(envelope)
        self._queue.put(envelope)
        return None

    def is_queue_full(self):
        return self._queue.qsize() >= AgentComConfiguration.MAX_QUEUED_MESSAGES

    def on(self, message_name, callback):
        self._register_callback(message_name, MessageCallback(callback, True))

    def once(self, message_name, callback):
        self._register_callback(message_name, MessageCallback(callback, False))

    def await_message(self, message_name):
        event = selectable_event.SelectableEvent()
        self.once(message_name, lambda _: event.set())

        return event

    def wait_for_ready(self, timeout=None):
        if not self._ready_event.wait(timeout):
            raise RookCommunicationException()
        else:
            if self._connection_error is not None:
                raise self._connection_error

    def _network_loop(self):
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
                    if not self._token_valid and e.status_code == 403:  # invalid token
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
            with self.await_message('InitialAugsCommand') as got_initial_augs_event:
                try:
                    self.run_until_stopped(got_initial_augs_event)
                except Exception as exc:
                    logger.exception("network loop stopped: %s", exc)

            if self._running:
                logger.debug("Reconnecting")

    def run_until_stopped(self, got_initial_augs_event):
        self._connection.ping()
        waiter = poll_select.Waiter([self._connection, self._queue, got_initial_augs_event], [], [self._connection])
        last_ping_time = 0
        last_read_time = time.time()
        got_initial_augs_started_waiting = time.time()
        got_initial_augs_keep_waiting = True
        while self._running:
            # this is similar to the select API: rlist, wlist, xlist - fds ready to read, ready to write, and errors
            # see official documentation for POSIX select or Python select.select for further info
            rlist, _, xlist = waiter.wait(AgentComConfiguration.PING_INTERVAL)

            # if it's time to send a ping, go ahead and do it now
            if (time.time() - last_ping_time) >= AgentComConfiguration.PING_INTERVAL:
                last_ping_time = time.time()
                logger.debug("Sending ping")
                self._connection.ping()
            # if rlist and xlist are empty -> the wait timed out, so check if we had a ping timeout
            if len(rlist) == 0 and len(xlist) == 0 and (
                    time.time() - last_read_time) >= AgentComConfiguration.PING_TIMEOUT:
                logger.debug("Disconnecting due to ping timeout")
                self._connection.close()
                break

            # got initial augs is ready, so don't wait on it anymore
            if got_initial_augs_event in rlist:
                # don't wait on got_initial_augs_event anymore
                got_initial_augs_keep_waiting = False
                waiter = poll_select.Waiter([self._connection, self._queue], [], [self._connection])
                logger.info("Finished initialization")
            # still waiting for got initial augs, but reached timeout, don't wait on it anymore
            if got_initial_augs_keep_waiting and (
                    time.time() - got_initial_augs_started_waiting) >= AgentComConfiguration.TIMEOUT:
                got_initial_augs_keep_waiting = False
                waiter = poll_select.Waiter([self._connection, self._queue], [], [self._connection])
                logger.warning("Timeout waiting for initial augs")
            # connection appeared in xlist, means it was closed
            if self._connection in xlist:
                logger.info("Connection closed")
                break
            # connection appeared in rlist, means there's data to read
            if self._connection in rlist:
                last_read_time = time.time()
                try:
                    code, msg = self._connection.recv_data(control_frame=True)
                    if code == websocket.ABNF.OPCODE_BINARY:
                        if msg is None:
                            # socket disconnected
                            logger.debug("Reading msg - socket disconnected")
                            break

                        if len(msg) > AgentComConfiguration.AGENT_COM_INCOMING_MAX_MESSAGE_SIZE:
                            logger.error("message length (%d) exceed max size", msg)
                            continue

                        envelope = envelope_pb.Envelope()
                        envelope.ParseFromString(msg)
                        self._handle_incoming_message(envelope)
                except (socket.error, websocket.WebSocketConnectionClosedException):
                    logger.debug("Reading msg - socket disconnected")
                    break
            # queue appeared in rlist, means there's a new message to send
            if self._queue in rlist:
                wrapped_envelope = None
                try:
                    wrapped_envelope = self._queue.get()
                    msg = wrapped_envelope.get_buffer()
                    if isinstance(msg, FlushMessagesEvent):
                        msg.event.set()
                        continue
                    self._connection.send_binary(msg)
                except (socket.error, websocket.WebSocketConnectionClosedException):
                    if wrapped_envelope is not None:
                        self._queue.put(wrapped_envelope)
                    logger.info("Got websocket closed exception")
                    break
                except Empty:
                    continue
                self._queue.messages_length - len(wrapped_envelope)

        logger.warning("loop stopped running")

    def flush_all_messages(self):
        flush_event = FlushMessagesEvent()
        self._queue.put(BasicEnvelopeWrapper(flush_event))
        flush_event.event.wait(AgentComConfiguration.FLUSH_TIMEOUT)

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
                              http_proxy_host=proxy_host, http_proxy_port=proxy_port)

        if os.environ.get('ROOKOUT_NO_HOST_HEADER_PORT') == '1':
            host = re.sub(':\d+$', '', urlparse(url).netloc)
        else:
            host = None

        connect_kwargs['sslopt'] = dict()

        if os.environ.get('ROOKOUT_SKIP_SSL_VERIFY') == '1':
            connect_kwargs['sslopt']['cert_reqs'] = ssl.CERT_NONE

        try:
            # connect using system certificates
            conn = websocket.create_connection(*connect_args, host=host, **connect_kwargs)
        # In some very specific scenario, you cannot
        # reference ssl.CertificateError because it does
        # exist, so instead we get with with getattr
        # (None never matches   an exception)
        except (ssl.SSLError, getattr(ssl, 'CertificateError', None)):
            # connect using certifi certificate bundle
            # (Python 2.7.15+ from python.org on macOS rejects our CA, see RK-3383)
            connect_kwargs['sslopt']['ca_certs'] = certifi.where()
            logger.debug("Got SSL error when connecting using system CA cert store, falling back to certifi")
            conn = websocket.create_connection(*connect_args, **connect_kwargs)
        # just in case there's a bug and we get stuck - timeout should never be hit since we always use select()
        conn.settimeout(30)
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
        if self._thread is not None:
            raise RuntimeError('Trying to start AgentCom thread twice')

        self._thread = threading.Thread(name="rookout-" + type(self).__name__, target=self._network_loop)
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
