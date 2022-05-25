import socket
import time
from typing import Optional

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.socket.SocketHandleThreadManager import SocketHandlerThreadManager
from nehushtan.socket.wormhole.NehushtanWormholeWorker import NehushtanWormholeWorker


class NehushtanWormhole:
    """
    Since 0.4.28
    """

    def __init__(self, port: int, dest_host: str, dest_port: int, log_dir: str = None):
        self.__listen_host = '0.0.0.0'
        self.__listen_port = port
        self.__dest_host = dest_host
        self.__dest_port = dest_port

        self.__wait_queue_size = 0
        self.__socket_instance: Optional[socket.socket] = None

        self.__thread_manager = SocketHandlerThreadManager()

        # logger: NehushtanFileLogger
        # self.__logger = logger
        self.__log_dir = log_dir
        self.__logger = NehushtanFileLogger("Wormhole", log_dir)

    def set_logger(self, logger: NehushtanFileLogger):
        self.__logger = logger
        return self

    def run(self):
        address_entries = socket.getaddrinfo(
            self.__listen_host,
            self.__listen_port,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
            0,
            socket.AI_PASSIVE
        )

        prepare_error = None

        for address_entry in address_entries:
            af, socktype, proto, canonname, sa = address_entry
            try:
                self.__socket_instance = socket.socket(af, socktype, proto)
                self.__socket_instance.bind(sa)
                self.__socket_instance.listen(self.__wait_queue_size)
            except OSError as msg:
                prepare_error = msg
                if self.__socket_instance is not None:
                    self.__socket_instance.close()
                self.__socket_instance = None
                continue
            break

        if self.__socket_instance is None:
            raise prepare_error

        # let the process of accept could be interupted (Since 0.4.17)
        self.__socket_instance.settimeout(1)

        self.__logger.notice(f"Wormhole Entrance is open, liston on {self.__listen_port}")

        self.__serving_thread()

    def __serving_thread(self):
        worker_thread_index = 0
        previous_alive_count = 0
        while True:
            alive_count = self.__thread_manager.check_alive_thread_count()
            if previous_alive_count != alive_count:
                self.__logger.info(f"NOW ALIVE CLIENT COUNT IS {alive_count}")
                previous_alive_count = alive_count

            try:
                connection, address = self.__socket_instance.accept()
                self.__logger.info(f"Accept New Client: {address}")
            except socket.timeout:
                continue

            worker_thread_index += 1

            socket_name = f"{time.time()}-{worker_thread_index}"
            worker = NehushtanWormholeWorker(socket_name, connection, address, self.__dest_host, self.__dest_port,
                                             self.__log_dir, self.__thread_manager)

            worker.work()

            # thread = Thread(
            #     target=worker.work,
            #     name=f"Worker#{worker_thread_index}"
            # )
            # self.__thread_manager.register_thread(thread)
            # thread.start()
