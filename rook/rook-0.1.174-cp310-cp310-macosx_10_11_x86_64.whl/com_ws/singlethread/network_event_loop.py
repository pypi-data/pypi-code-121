import socket
import time

import websocket
from rook.com_ws.flush_messages_event import FlushMessagesEvent

from rook.logger import logger
import rook.protobuf.envelope_pb2 as envelope_pb
from rook.config import AgentComConfiguration
import rook.com_ws.poll_select as poll_select


class NetworkEventLoop(object):
    def __init__(self, connection, outgoing_queue, handle_incoming_msg, got_initial_augs_event):
        self._running = True
        self._connection = connection
        self._queue = outgoing_queue
        self._handle_incoming_msg = handle_incoming_msg
        self._got_initial_augs_event = got_initial_augs_event

    def run_until_stopped(self):
        self._connection.ping()
        waiter = poll_select.Waiter([self._connection, self._queue, self._got_initial_augs_event], [], [self._connection])
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
            if self._got_initial_augs_event in rlist:
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
                logger.debug("Connection closed")
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
                        self._handle_incoming_msg(envelope)
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
                    break
                self._queue.messages_length - len(wrapped_envelope)

    def stop(self):
        self._running = False
        self._connection.close(1000)

