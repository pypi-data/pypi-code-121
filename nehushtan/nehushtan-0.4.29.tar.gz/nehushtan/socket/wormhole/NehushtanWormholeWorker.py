import socket
import time
from threading import Thread
from typing import Optional

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.socket.SocketHandleThreadManager import SocketHandlerThreadManager


class NehushtanWormholeWorker:
    """
    Since 0.4.28
    """

    def __init__(self,
                 socket_name: str,
                 upstream_socket: socket.socket, upstream_address,
                 downstream_host: str, downstream_port: int,
                 log_dir: str = None,
                 thread_manager: SocketHandlerThreadManager = None
                 ):
        self.__socket_name = socket_name

        self.__upstream_socket = upstream_socket
        self.__upstream_address = upstream_address

        self.__downstream_socket: Optional[socket.socket] = None
        self.__downstream_host = downstream_host
        self.__downstream_port = downstream_port

        # self.__upstream_socket.settimeout(1)
        # self.__downstream_socket.settimeout(1)

        # self.__data_queue_from_upstream = Queue()
        # self.__data_queue_from_downstream = Queue()

        # socket_name = f"{time.time()}#{CommonHelper.generate_random_uuid_hex()}"
        self.__logger = NehushtanFileLogger(f"WormholeSocket/{socket_name}", log_dir)
        self.__logger.notice(f"From {upstream_address}")

        self.__thread_manager = thread_manager

    def set_logger(self, logger: NehushtanFileLogger):
        self.__logger = logger
        return self

    def work(self):
        address_entries = socket.getaddrinfo(
            self.__downstream_host,
            self.__downstream_port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )

        prepare_error = None

        for address_entry in address_entries:
            af, socktype, proto, canonname, sa = address_entry
            try:
                self.__downstream_socket = socket.socket(af, socktype, proto)
                self.__downstream_socket.connect(sa)
            except OSError as msg:
                prepare_error = msg
                if self.__downstream_socket is not None:
                    self.__downstream_socket.close()
                self.__downstream_socket = None
                continue
            break

        if self.__downstream_socket is None:
            raise prepare_error

        self.__logger.info(f"Downstream Socket Connected to {self.__downstream_socket.getpeername()}")

        thread_reading_upstream = Thread(
            target=self.thread_body_reading_upstream,
            name=f"{self.__socket_name}::upstream_monitor",
            daemon=True
        )
        thread_reading_downstream = Thread(
            target=self.thread_body_reading_downstream,
            name=f"{self.__socket_name}::downstream_monitor",
            daemon=True
        )

        thread_reading_upstream.start()
        thread_reading_downstream.start()

        self.__logger.info("Two reading threads started")

        self.__thread_manager.register_thread(thread_reading_upstream)
        self.__thread_manager.register_thread(thread_reading_downstream)

        self.__logger.debug("registered two threads and finish work method")

    @staticmethod
    def read_all_available_from_socket(stream_socket: socket.socket, buffer_size: int, logger: NehushtanFileLogger):
        total_buffer = b""
        while True:
            try:
                buffer = stream_socket.recv(buffer_size, socket.MSG_DONTWAIT)
                if len(buffer) <= 0:
                    break
                logger.debug(f"read_all_available_from_socket one piece of {len(buffer)} bytes")
                total_buffer += buffer
                time.sleep(0.1)
            except BlockingIOError:
                if len(total_buffer) > 0:
                    break
                else:
                    raise
        return total_buffer

    def thread_body_reading_upstream(self):
        while True:
            # self.__logger.debug("thread_body_reading_upstream routine start")
            try:
                buffer = self.read_all_available_from_socket(self.__upstream_socket, 1024, self.__logger)
                # buffer = self.__upstream_socket.recv(1024, socket.MSG_DONTWAIT)
                if len(buffer) <= 0:
                    break
                self.__logger.info(f"Read {len(buffer)} bytes from upstream")
            except BlockingIOError:
                # self.__logger.debug(f"thread_body_reading_upstream met BlockingIOError, sleep")
                time.sleep(1)
                continue
            except OSError:
                self.__logger.error("Upstream Dead")
                break

            self.__logger.write_raw_line_to_log(f"{buffer}")
            try:
                write_byte_count = self.__downstream_socket.send(buffer)
                if write_byte_count > 0:
                    self.__logger.info(f"Wrote {write_byte_count} bytes to downstream")
                else:
                    self.__logger.error(f"Failed to write into downstream")
                    break
            except OSError:
                self.__logger.error("Upstream Dead")
                break

        self.__logger.notice("CLOSE SOCKETS")
        self.__downstream_socket.close()
        self.__upstream_socket.close()

    def thread_body_reading_downstream(self):
        while True:
            # self.__logger.debug("thread_body_reading_downstream routine start")
            try:
                buffer = self.read_all_available_from_socket(self.__downstream_socket, 1024, self.__logger)
                # buffer = self.__downstream_socket.recv(1024, socket.MSG_DONTWAIT)

                if len(buffer) <= 0:
                    break

                self.__logger.info(f"Read {len(buffer)} bytes from downstream")

            except BlockingIOError:
                # self.__logger.debug(f"thread_body_reading_downstream met BlockingIOError, sleep")
                time.sleep(1)
                continue
            except OSError:
                self.__logger.error("Downstream Dead")
                break

            self.__logger.write_raw_line_to_log(f"{buffer}")
            try:
                write_byte_count = self.__upstream_socket.send(buffer)
                if write_byte_count > 0:
                    self.__logger.info(f"Write {write_byte_count} bytes to upstream")
                else:
                    self.__logger.error(f"Failed to write into upstream")
                    break
            except OSError:
                self.__logger.error("Upstream Dead")
                break

        self.__logger.notice("CLOSE SOCKETS")
        self.__downstream_socket.close()
        self.__upstream_socket.close()
