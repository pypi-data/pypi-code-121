from collections import deque
from time import sleep

import zmq

from kamzik3.constants import WORKER_READY, MSG_TERMINATE, MSG_EMPTY


class Worker:
    """
    This is General Worker Class which can be used as a Server Worker.
    """

    running = False  # Worker running state

    def __init__(self, id, master_host, master_port, zmq_context=None):
        """
        Initiate new Worker.
        Each Worker connects to Master server.
        Worker can perform only instructions defined in instructions_set list.
        :param str id: Worker ID
        :param str master_host:  Host of master server
        :param int master_port: Port of master server
        :param Context zmq_context: ZMQ context
        """
        self.instructions_set = []
        self.zmq_context = zmq_context
        self.master_host = master_host
        self.master_port = master_port
        self.id = id.encode()

    def _init_socket(self):
        """
        Initiate connection to the master server.
        """
        if self.zmq_context is None:
            self.zmq_context = zmq.Context.instance()

        self.socket_worker = self.zmq_context.socket(zmq.REQ)
        self.socket_worker.setsockopt(zmq.IDENTITY, self.id)
        self.socket_worker.connect(
            "tcp://{}:{}".format(self.master_host, self.master_port)
        )

    def run(self):
        """
        Start workers main loop.
        """
        self.running = True
        self._init_socket()
        self.socket_worker.send_multipart([WORKER_READY] + self.instructions_set)
        while self.running:
            request = self.socket_worker.recv_multipart()
            if request[2] == MSG_TERMINATE:
                self.stop()
                continue
            self.socket_worker.send_multipart(
                request[:2] + self.get_payload(request[2:])
            )
        self.socket_worker.close()

    def get_payload(self, request):
        """
        This method gets input data and perform instruction which must be part of the request.
        This function must be implemented in every Worker.
        :param list request: input data
        :return:
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop Worker.
        Set running state to False.
        """
        self.running = False


class BalancedServer:
    """
    This is main server, which can perform multiple different tasks.
    It's main function is to serve reply to every request of client.
    Every request is passed to the free worker.
    Worker process request, generate reply and server is returning reply to the client.
    In current implementation only one type of worker is supported.
    So one server can serve onl;y one purpose.
    For example acting as a Device Server or File Server.
    Functionality is determined by Worker defined by worker_class.
    """

    running = False  # Server running state

    def __init__(self, host, port, workers_count=5, worker_class=Worker):
        """
        Initiate new Server.
        Functionality is determined by workers.
        :param str host: host
        :param int port: port
        :param int workers_count: Number of workers spawn by server
        :param Class worker_class: Class of Worker
        """
        self.zmq_context = zmq.Context.instance()
        self.host = host
        self.port = port
        self.socket_frontend = None
        self.socket_backend = None
        self.port_backend = None
        self.workers_count = workers_count
        self.worker_class = worker_class
        self.poller = zmq.Poller()
        self.registered_workers = {}
        self.local_workers = []
        self.idle_workers = []

    def _init_frontend(self):
        """
        Initiate frontend part of the server.
        This is visible to the external clients.
        """
        self.socket_frontend = self.zmq_context.socket(zmq.ROUTER)
        self.socket_frontend.setsockopt(
            zmq.IDENTITY, "FE@{}:{}".format(self.host, self.port).encode()
        )
        self.socket_frontend.bind("tcp://{}:{}".format(self.host, self.port))

    def _init_backend(self):
        """
        Initiate backend part of the server.
        This is visible to the workers only.
        """
        self.socket_backend = self.zmq_context.socket(zmq.ROUTER)
        self.socket_backend.setsockopt(
            zmq.IDENTITY, "BE@{}:{}".format(self.host, self.port).encode()
        )
        self.port_backend = self.socket_backend.bind_to_random_port(
            "tcp://{}".format(self.host)
        )
        self.poller.register(self.socket_backend, zmq.POLLIN)

    def _init_workers(self):
        """
        Spawn workers connected to the server backend.
        """
        for i in range(self.workers_count):
            worker = self.worker_class(
                "W_{}".format(i), self.host, self.port_backend, self.zmq_context
            )
            self.local_workers.append(worker)
            worker.start()

    def run(self):
        """
        Start main server loop.
        """
        self.running = True

        # Initiate Frontend, Backend and workers
        self._init_frontend()
        self._init_backend()
        self._init_workers()

        # Start the server
        self.main_loop()

        # Close Frontend and Backend
        self.socket_backend.close()
        self.socket_frontend.close()

    def main_loop(self):
        """
        Main server loop.
        Run until running state is True.
        Poll for Backend and Frontend sockets with any message to read.
        """
        while self.running:
            sockets = dict(self.poller.poll(timeout=10))

            if self.socket_backend in sockets:
                # Handle worker activity on the backend
                request = self.socket_backend.recv_multipart()
                worker, _, client = request[:3]
                if not self.idle_workers:
                    # Poll for clients now that a worker is available
                    self.poller.register(self.socket_frontend, zmq.POLLIN)
                self.idle_workers.append(worker)

                if client != WORKER_READY:
                    # If client reply, send rest back to frontend
                    self.socket_frontend.send_multipart([client] + request[3:])
                else:
                    self.registered_workers[worker] = request[3:]

            if self.socket_frontend in sockets:
                # Get next client request, route to last-used worker
                request = self.socket_frontend.recv_multipart()

                worker = self.idle_workers.pop(0)
                instruction = request[2]
                self.socket_backend.send_multipart([worker, MSG_EMPTY] + request)
                if not self.idle_workers:
                    # Don't poll clients if no workers are available
                    self.poller.unregister(self.socket_frontend)

    def stop(self):
        """
        Stop server main loop.
        Also Terminate every worker on the server.
        """
        for worker in self.local_workers:
            # Send Terminate message to every worker
            self.socket_backend.send_multipart(
                [worker.id, MSG_EMPTY, MSG_EMPTY, MSG_EMPTY, MSG_TERMINATE]
            )

        self.local_workers = []
        self.running = False


class Publisher:
    """
    Simple Publisher loop.
    It's purpose is to collect all messages in the queue and then push it to the socket.
    This is general class for any Publisher.
    _publish_message must be reimplemented.
    """

    running = False  # Publisher running state

    def __init__(self, host, port, zmq_context=None):
        """
        Initiate Publisher.
        :param str host: host
        :param int port: port
        :param Context zmq_context: ZMQ Context
        """
        self.zmq_context = zmq_context
        if self.zmq_context is None:
            self.zmq_context = zmq.Context.instance()
        self.host = host
        self.port = port
        self.messages_queue = deque()
        self._init_socket()

    def _init_socket(self):
        """
        Initiate Publisher socket.
        Use zmq.PUB as we are using PUB -> SUB socket pair.
        """
        self.socket_publisher = zmq.Context.instance().socket(zmq.PUB)
        self.socket_publisher.setsockopt(zmq.IDENTITY, b"P_0")
        self.socket_publisher.bind("tcp://{}:{}".format(self.host, self.port))

    def _publish_message(self, header, message):
        """
        This method is called to publish the message.
        It must be reimplemented in final class.
        :param str header: Header of the message
        :param mixed message: Message depends on the communication protocol
        """
        raise NotImplementedError()

    def run(self):
        """
        Main Publisher loop.
        Until running state is True, publish all messages from the messages_queue.
        :return:
        """
        timeout = 0.005
        self.running = True
        while self.running:
            while self.messages_queue:
                self._publish_message(*self.messages_queue.popleft())
            sleep(timeout)

    def push_message(self, header, message, token=None):
        """
        Push new message into the message queue
        :param str header: Header of the message
        :param mixed message: Message depends on the communication protocol
        :param int token: message token
        """
        try:
            if token is not None:
                header += "." + str(token)
            self.messages_queue.append((header, message))
        except TypeError:
            self.logger.exception("Error pushing message to client")

    def stop(self):
        """
        Stop Publisher loop.
        """
        self.running = False
