import logging
import os
import time
from collections import OrderedDict
from copy import copy
from multiprocessing import Process
from threading import Thread
from typing import Optional, Any

import numpy as np
import zmq

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsZmq import BalancedServer, Worker


# Method "get_payload" is abstract and doesn't get overwritten here, but that's "okay", since the "run" method doesn't
# call "get_payload". IMO: bad class design.
# pylint: disable=abstract-method
class FileWorker(Worker, Process):
    def __init__(
        self,
        id,
        master_host,
        master_port,
        worker_host,
        worker_port=None,
        zmq_context=None,
    ):
        Process.__init__(self)
        Worker.__init__(self, id, master_host, master_port, zmq_context)
        if not hasattr(self, "logger"):
            self.logger = logging.getLogger("Device.{}".format(id))
        self.worker_host = worker_host
        self.worker_port = worker_port
        self.socket: Optional[zmq.Socket] = None
        # Any not specific enough here
        self.master_address: Optional[Any] = None

    def _init_socket(self):
        if self.zmq_context is None:
            self.zmq_context = zmq.Context.instance()

        self.socket = self.zmq_context.socket(zmq.ROUTER)
        # Probe router ensures, that handshake is initiated after router is connected to other socket
        self.socket.probe_router = 1
        self.socket.setsockopt(zmq.IDENTITY, self.id)
        self.socket.setsockopt(zmq.LINGER, -1)
        if self.worker_port is None:
            self.worker_port = self.socket.bind_to_random_port(
                "tcp://{}".format(self.worker_host)
            )
        else:
            self.socket.bind("tcp://{}:{}".format(self.worker_host, self.worker_port))
        # Connect to Master host:port
        self.socket.connect("tcp://{}:{}".format(self.master_host, self.master_port))

    def run(self):
        self.running = True
        self._init_socket()
        # Wait for ACK from Master
        self.master_address, _, message = self.socket.recv_multipart()

        if message == MSG_ACK:
            # Run until we got MSG_TERMINATE from Master
            while self.running:
                current_task = self.socket.recv_multipart()
                if len(current_task) == 3 and current_task[2] == MSG_TERMINATE:
                    self.stop()
                elif current_task[4] == INSTRUCTION_PUSH:
                    self.task_push(current_task)
                elif current_task[4] in (INSTRUCTION_PULL, INSTRUCTION_SYNC):
                    self.task_pull(current_task)
                elif current_task[4] == INSTRUCTION_FORWARD:
                    self.task_forward(current_task)

    def task_forward(self, task_data):
        self.socket.send_multipart(
            [
                task_data[0],
                MSG_EMPTY,
                MSG_FORWARD,
                task_data[2],
                self.worker_host.encode(),
                str(self.worker_port).encode(),
                task_data[-1],
            ]
        )
        writer_address, _ = self.socket.recv_multipart()
        drive, source_file, remote_host, remote_port = task_data[5:9]
        self.logger.info(
            "Forwarding file {}:{}".format(drive.decode(), source_file.decode())
        )
        # Connect to remote host
        self.socket.connect(
            "tcp://{}:{}".format(remote_host.decode(), remote_port.decode())
        )
        remote_address, _, message = self.socket.recv_multipart()

        if message == MSG_ACK:
            # Request new Read Task
            self.socket.send_multipart(
                [remote_address, MSG_EMPTY, INSTRUCTION_PUSH, drive, source_file]
            )
            # Obtain Reader credentials
            _, _, reader_host, reader_port, _reader_task = self.socket.recv_multipart()
            # Connect to Reader
            self.socket.connect(
                "tcp://{}:{}".format(reader_host.decode(), reader_port.decode())
            )
            # Finishing handshake with Reader
            reader_address, _ = self.socket.recv_multipart()
            # Waiting for metadata from Reader
            file_metadata = self.socket.recv_multipart()
            # Send file metadata to writer
            self.socket.send_multipart(
                [writer_address, MSG_EMPTY] + file_metadata[2:], copy=False
            )
            # Wait for ACK from Writer
            self.socket.recv_multipart()

            aborted = False
            progress_sync_threshold, sync_increment = 5, 5
            message = None
            while True:
                if message is None:
                    # Notify Reader, that we are ready to receive file chunk
                    self.socket.send_multipart(
                        [reader_address, MSG_EMPTY, WORKER_READY]
                    )
                    # Read file chunk from Reader
                    message = self.socket.recv_multipart()

                # Stop writing on EOF
                if len(message) == 2:
                    self.socket.send_multipart([reader_address, MSG_EMPTY, WORKER_DONE])
                    break
                elif message[0] == self.master_address and message[2] == MSG_ABORT:
                    # Wait for ACK from writer
                    self.socket.recv_multipart()
                    # Notify reader, that task was Aborted
                    self.socket.send_multipart([reader_address, MSG_EMPTY, MSG_ABORT])
                    # Wait for ACK from reader
                    self.socket.recv_multipart()
                    # Notify reader, that task was Aborted
                    self.socket.send_multipart([writer_address, MSG_EMPTY, MSG_ABORT])
                    # Wait for ACK from reader
                    self.socket.recv_multipart()
                    # Reply back to Master with ACK
                    self.socket.send_multipart(
                        [self.master_address, MSG_EMPTY, MSG_ACK]
                    )
                    aborted = True
                    break
                elif message[0] == reader_address and message[2] == MSG_ABORT:
                    # Notify Master, that task was aborted
                    self.socket.send_multipart(
                        [self.master_address, MSG_EMPTY, MSG_ABORT, task_data[-1]]
                    )
                    # Wait for ACK from Master
                    self.socket.recv_multipart()
                    # Notify reader, that task was Aborted
                    self.socket.send_multipart([writer_address, MSG_EMPTY, MSG_ABORT])
                    # Wait for ACK from reader
                    self.socket.recv_multipart()
                    # Reply back to Reader with ACK
                    self.socket.send_multipart([reader_address, MSG_EMPTY, MSG_ACK])
                    aborted = True
                    break
                elif message[0] == writer_address and message[2] == MSG_ABORT:
                    # Notify Master, that task was aborted
                    self.socket.send_multipart(
                        [self.master_address, MSG_EMPTY, MSG_ABORT, task_data[-1]]
                    )
                    # Wait for ACK from Master
                    self.socket.recv_multipart()
                    # Notify reader, that task was Aborted
                    self.socket.send_multipart([reader_address, MSG_EMPTY, MSG_ABORT])
                    # Wait for ACK from reader
                    self.socket.recv_multipart()
                    # Reply back to Reader with ACK
                    self.socket.send_multipart([writer_address, MSG_EMPTY, MSG_ACK])
                    aborted = True
                    break

                self.socket.send_multipart(
                    [writer_address, MSG_EMPTY] + message[2:], copy=False
                )
                # Wait for ACK from Writer
                ack = self.socket.recv_multipart()
                if ack[0] == writer_address and ack[2] == WORKER_READY:
                    # Check if we should sync progress with server
                    if float(message[3].decode()) >= progress_sync_threshold:
                        self.socket.send_multipart(
                            [
                                self.master_address,
                                MSG_EMPTY,
                                MSG_PROGRESS,
                                task_data[-1],
                                message[3],
                            ]
                        )
                        progress_sync_threshold += sync_increment
                    message = None
                else:
                    message = ack

            if not aborted:
                message = self.socket.recv_multipart()
                if message[2] == MSG_ACK:
                    self.socket.send_multipart([writer_address, MSG_EMPTY], copy=False)
                    writer_addr, _, status = self.socket.recv_multipart()
                    if status == WORKER_DONE:
                        self.socket.send_multipart(
                            [writer_addr, MSG_EMPTY, MSG_ACK], copy=False
                        )
                        self.socket.send_multipart(
                            [self.master_address, MSG_EMPTY, WORKER_DONE, task_data[-1]]
                        )

            # Close connection to Reader
            self.socket.disconnect(
                "tcp://{}:{}".format(reader_host.decode(), reader_port.decode())
            )
            # Close connection to remote File server
            self.socket.disconnect(
                "tcp://{}:{}".format(remote_host.decode(), remote_port.decode())
            )

    def task_push(self, task_data):
        # Reply to Master and forward reply to original client
        self.socket.send_multipart(
            [
                task_data[0],
                MSG_EMPTY,
                MSG_FORWARD,
                task_data[2],
                self.worker_host.encode(),
                str(self.worker_port).encode(),
                task_data[-1],
            ]
        )
        # Wait for writer and finish handshake
        writer_address, _ = self.socket.recv_multipart()
        source_file = task_data[6].decode()
        file_size = os.path.getsize(source_file)
        file_mod_time = os.path.getmtime(source_file)
        chunk_size = int(5e5)
        self.logger.info("Pushing file {}".format(source_file))
        # Send file metadata to writer
        self.socket.send_multipart(
            [
                writer_address,
                MSG_EMPTY,
                source_file.encode(),
                str(file_size).encode(),
                str(file_mod_time).encode(),
                str(chunk_size).encode(),
            ],
            copy=False,
        )

        chunks_send = 0
        bytes_send = 0
        aborted = False
        progress_sync_threshold, sync_increment = 5, 5
        with open(source_file, "rb") as fp:
            while self.running:
                message = self.socket.recv_multipart()
                if message[0] == self.master_address and message[2] == MSG_ABORT:
                    # Wait until writer is ready
                    self.socket.recv_multipart()
                    # Notify writer that task is aborted
                    self.socket.send_multipart([writer_address, MSG_EMPTY, MSG_ABORT])
                    # Get ACK from writer
                    self.socket.recv_multipart()
                    # Reply back to master with ACK
                    self.socket.send_multipart(
                        [self.master_address, MSG_EMPTY, MSG_ACK]
                    )
                    aborted = True
                    break
                elif message[0] == writer_address and message[2] == MSG_ABORT:
                    # Notify Master, that task was aborted
                    self.socket.send_multipart(
                        [self.master_address, MSG_EMPTY, MSG_ABORT, task_data[-1]]
                    )
                    # Get ACK from Master
                    self.socket.recv_multipart()
                    # Reply back to writer, that task was aborted
                    self.socket.send_multipart([writer_address, MSG_EMPTY, MSG_ACK])
                    aborted = True
                    break
                # Read chunk from file
                data = fp.read(chunk_size)
                # No data = EOF
                if not data:
                    self.socket.send_multipart([writer_address, MSG_EMPTY], copy=False)
                    break
                chunks_send += 1
                bytes_send += len(data)
                # Calculate read progress
                progress = (bytes_send / file_size) * 100
                # Send data chunk to writer
                self.socket.send_multipart(
                    [writer_address, MSG_EMPTY, data, str(progress).encode()],
                    copy=False,
                )
                # Check if we should sync progress with server
                if progress >= progress_sync_threshold:
                    # Sync progress with server
                    self.socket.send_multipart(
                        [
                            self.master_address,
                            MSG_EMPTY,
                            MSG_PROGRESS,
                            task_data[-1],
                            str(progress).encode(),
                        ]
                    )
                    # Set next progress threshold
                    progress_sync_threshold += sync_increment

        # Push Task was finished successfully
        if not aborted:
            writer_addr, _, status = self.socket.recv_multipart()
            if status == WORKER_DONE:
                self.socket.send_multipart(
                    [writer_addr, MSG_EMPTY, MSG_ACK], copy=False
                )
                self.socket.send_multipart(
                    [self.master_address, MSG_EMPTY, WORKER_DONE, task_data[-1]]
                )

    def task_pull(self, task_data):
        # If client and worker_id is equal, don't reply back to master
        if task_data[2] != self.id:
            # Reply to Master with info that should be forwarded to future Writer
            self.socket.send_multipart(
                [
                    self.master_address,
                    MSG_EMPTY,
                    MSG_FORWARD,
                    task_data[2],
                    self.id,
                    task_data[-1],
                ]
            )
        remote_host, remote_port, drive, source_file, dest_file, task_id = task_data[5:]
        self.logger.info(
            "Pulling file {}:{} and saving to {}".format(
                drive.decode(), source_file.decode(), dest_file.decode()
            )
        )
        # Connect to remote File server
        self.socket.connect(
            "tcp://{}:{}".format(remote_host.decode(), remote_port.decode())
        )
        # Get acknowledge response from remote File server
        remote_address, _, message = self.socket.recv_multipart()
        if message == MSG_ACK:
            # Request new Read Task
            self.socket.send_multipart(
                [remote_address, MSG_EMPTY, INSTRUCTION_PUSH, drive, source_file]
            )
            # Obtain Reader credentials
            _, _, reader_host, reader_port, _reader_task = self.socket.recv_multipart()
            # Connect to Reader
            self.socket.connect(
                "tcp://{}:{}".format(reader_host.decode(), reader_port.decode())
            )
            # Finishing handshake with Reader
            reader_address, _ = self.socket.recv_multipart()
            # Waiting for metadata from Reader
            (
                _,
                _,
                source_file_path,
                _file_size,
                file_mod_time,
                _chunk_size,
            ) = self.socket.recv_multipart()

            chunks_received = 0
            bytes_received = 0
            aborted = False
            progress_sync_threshold, sync_increment = 5, 5
            # Create or overwrite destination file
            with open(dest_file, "wb") as fp:
                # Notify reader that socket is ready to acquire file content
                while True:
                    # Notify Reader, that we are ready to receive file chunk
                    self.socket.send_multipart(
                        [reader_address, MSG_EMPTY, WORKER_READY]
                    )
                    # Read file chunk from Reader
                    message = self.socket.recv_multipart()
                    # Stop writing on EOF
                    if len(message) == 2:
                        self.socket.send_multipart(
                            [reader_address, MSG_EMPTY, WORKER_DONE]
                        )
                        break
                    elif message[0] == self.master_address and message[2] == MSG_ABORT:
                        # Notify reader, that task was Aborted
                        self.socket.send_multipart(
                            [reader_address, MSG_EMPTY, MSG_ABORT]
                        )
                        # Wait for ACK from reader
                        self.socket.recv_multipart()
                        # Reply back to Master with ACK
                        self.socket.send_multipart(
                            [self.master_address, MSG_EMPTY, MSG_ACK]
                        )
                        aborted = True
                        break
                    elif message[0] == reader_address and message[2] == MSG_ABORT:
                        # Notify Master, that task was aborted
                        self.socket.send_multipart(
                            [self.master_address, MSG_EMPTY, MSG_ABORT, task_data[-1]]
                        )
                        # Wait for ACK from Master
                        self.socket.recv_multipart()
                        # Reply back to Reader with ACK
                        self.socket.send_multipart([reader_address, MSG_EMPTY, MSG_ACK])
                        aborted = True
                        break
                    chunks_received += 1
                    bytes_received += len(message[2])
                    fp.write(message[2])
                    # Check if we should sync progress with server
                    if float(message[3].decode()) >= progress_sync_threshold:
                        self.socket.send_multipart(
                            [
                                self.master_address,
                                MSG_EMPTY,
                                MSG_PROGRESS,
                                task_id,
                                message[3],
                            ]
                        )
                        progress_sync_threshold += sync_increment

            if not aborted:
                os.utime(
                    dest_file,
                    (float(file_mod_time.decode()), float(file_mod_time.decode())),
                )
                message = self.socket.recv_multipart()
                if message[2] == MSG_ACK:
                    self.socket.send_multipart(
                        [
                            self.master_address,
                            MSG_EMPTY,
                            WORKER_DONE,
                            task_id,
                            source_file_path,
                        ]
                    )
            else:
                # Remove partial file
                os.remove(dest_file)

            # Close connection to Reader
            self.socket.disconnect(
                "tcp://{}:{}".format(reader_host.decode(), reader_port.decode())
            )
            # Close connection to remote File server
            self.socket.disconnect(
                "tcp://{}:{}".format(remote_host.decode(), remote_port.decode())
            )


class DeviceFileServer(Device, BalancedServer, Thread):
    max_task_history = 5

    def __init__(
        self,
        device_id,
        host,
        port,
        workers_count=5,
        worker_class=FileWorker,
        config=None,
    ):
        self.task_counter = (i for i in range(2**63))
        Thread.__init__(self)
        BalancedServer.__init__(self, host, port, workers_count, worker_class)
        Device.__init__(self, device_id, config)
        self.frontend_connector = zmq.Context.instance().socket(zmq.REQ)
        self.frontend_connector.connect("tcp://{}:{}".format(host, port))
        self.backend_connector = zmq.Context.instance().socket(zmq.REQ)
        self.connect()

    def handle_configuration(self):
        # Doesn't do anything, but is abstract in Device, so override empty here
        pass

    def _init_workers(self):
        for i in range(self.workers_count):
            worker = self.worker_class(
                "W_{}@{}:{}".format(i, self.host, self.port),
                self.host,
                self.port_backend,
                self.host,
            )
            self.local_workers.append(worker)
            worker.start()

    def main_loop(self):
        """
        This is main loop of Fileserver.

        First connect backend_connector.
        Then poll for messages waiting for sockets to be processed.
        First check if there is any message waiting in backend, then check frontend socket.
        """
        self.backend_connector.connect(
            "tcp://{}:{}".format(self.host, self.port_backend)
        )
        while self.running:
            # Poll sockets with 10ms timeout
            sockets = dict(self.poller.poll(timeout=10))

            if self.socket_backend in sockets:
                # Handle worker activity on the backend
                request = self.socket_backend.recv_multipart()
                if len(request) == 2:
                    # Worker connected for the first time
                    self._worker_idle(request[0])
                    # Send ACK to worker
                    self.socket_backend.send_multipart([request[0], MSG_EMPTY, MSG_ACK])
                    continue

                worker_address, _ = request[:2]
                if request[2] == MSG_FORWARD:
                    # Forward reply from worker to original client
                    self.set_task_status(request[-1].decode(), STATUS_BUSY)
                    # Task was accepted
                    self.socket_frontend.send_multipart(
                        [request[3], MSG_EMPTY] + request[4:]
                    )
                elif request[2] == MSG_PROGRESS:
                    # Task progress was updated
                    self.set_task_progress(
                        request[3].decode(), float(request[4].decode())
                    )
                elif request[2] == WORKER_DONE:
                    task_id = request[3].decode()
                    if self.get_value([task_id, ATTR_TASK_INSTRUCTION]) == "Sync files":
                        # If task is to sync file continue with next file
                        if self._sync_next_file(
                            task_id, request[0], request[4].decode()
                        ):
                            continue
                    # Task is done
                    self.set_task_status(task_id, STATUS_IDLE)
                    self.set_value([task_id, ATTR_FINISHED_AT], time.time())
                    self._worker_idle(request[0])
                elif request[2] == MSG_ABORT:
                    self.socket_backend.send_multipart([request[0], MSG_EMPTY, MSG_ACK])
                    worker_address = self.get_value([request[3].decode(), ATTR_WORKER])
                    if worker_address.encode() != request[0]:
                        self.socket_backend.send_multipart(
                            [worker_address.encode(), MSG_EMPTY, MSG_ABORT, request[3]]
                        )
                    self.abort_task(request[3].decode())
                    self._worker_idle(worker_address.encode())
                elif request[2] == MSG_ACK:
                    pass

            if self.socket_frontend in sockets:
                # Get next client request, route to last-used worker
                request = self.socket_frontend.recv_multipart()
                if len(request) == 2:
                    self.socket_frontend.send_multipart(
                        [request[0], MSG_EMPTY, MSG_ACK]
                    )
                    continue
                # on_fs is declared in deviceVirtualDirectory, so we probably want an abstract method "on_fs" in
                # deviceFileServer, but in the meantime, disable the warning
                # pylint: disable=no-member
                if request[2] == INSTRUCTION_PUSH and not self.on_fs(
                    request[3].decode(), request[4].decode()
                ):
                    request[2] = INSTRUCTION_FORWARD
                    source = self.get_value(ATTR_DRIVES)[request[3].decode()]["source"]
                    request += [
                        source.get_value(ATTR_HOST).encode(),
                        str(source.get_value(ATTR_PORT)).encode(),
                    ]

                worker = self.idle_workers.pop(0)
                task_id = self.add_task(worker.decode(), request)

                if request[2] == INSTRUCTION_SYNC:
                    self.socket_frontend.send_multipart(
                        [request[0], MSG_EMPTY, worker, task_id.encode()]
                    )
                    if not self._sync_next_file(task_id, worker):
                        self.set_task_status(task_id, STATUS_IDLE)
                        self.idle_workers.insert(0, worker)
                else:
                    self.socket_backend.send_multipart(
                        [worker, MSG_EMPTY] + request + [task_id.encode()]
                    )
                self._check_idle_workers()

    def _worker_idle(self, worker_id):
        """
        We have free worker, so push it back to idle_workers list.

        :param worker_id: str
        """
        self.idle_workers.append(worker_id)
        self._check_idle_workers()

    def _check_idle_workers(self):
        """
        Check if worker is IDLE.

        If so, make sure that fronted is reading requests.
        Otherwise remove fronted from poller.
        """
        if self.idle_workers:
            # Poll for clients now that a worker is available
            self.poller.register(self.socket_frontend, zmq.POLLIN)
        else:
            # Unregister fronted socket from polling, no free worker available
            self.poller.unregister(self.socket_frontend)

    def _sync_next_file(self, task_id, worker_id, synced_file=None):
        """
        This is specific to sync request.

        When multiple files are requested, sync Task uses one worker to sync files one by one.
        At each call, function determine which files are already synced and which still remains.
        If next file needs to be synced True is returned False otherwise.

        :param task_id: str
        :param worker_id: str
        :return: bool
        """
        self.set_value([task_id, ATTR_STATUS], STATUS_BUSY)
        requested_files = self.get_value([task_id, ATTR_REQUESTED_FILES])
        synced_files = OrderedDict()

        for drive, path in self.get_value([task_id, ATTR_REQUESTED_FILES]):
            input_dir, file_name = os.path.split(path)
            # get_local_path is declared in deviceVirtualDirectory, so we probably want an abstract method "on_fs" in
            # deviceFileServer, but in the meantime, disable the warning
            # pylint: disable=no-member
            synced, local_path = self.get_local_path(drive, input_dir, file_name)
            # File was downloaded
            # What can happened is that file updated while checked for sync again
            # To avoid that I always assume that file is in sync when downloaded and existing on local FS
            if synced or path == synced_file:
                synced_files[(drive, path)] = local_path

        self.set_value([task_id, ATTR_SYNCED_FILES], synced_files)

        remaining_files = set(requested_files) - set(synced_files.keys())
        if len(remaining_files) > 0:
            drive, path = remaining_files.pop()
            input_dir, file_path = os.path.split(path)
            drive_meta = self.get_value(ATTR_DRIVES)[drive]
            source = drive_meta.get("source")
            # is_cached is declared in deviceVirtualDirectory, so we probably want an abstract method "on_fs" in
            # deviceFileServer, but in the meantime, disable the warning
            # pylint: disable=no-member
            _cached, cache_path = self.is_cached(drive, input_dir, file_path)
            self.logger.info("Syncing file {}:{}".format(drive, path))
            self.socket_backend.send_multipart(
                [
                    worker_id,
                    MSG_EMPTY,
                    worker_id,
                    MSG_EMPTY,
                    INSTRUCTION_SYNC,
                    source.get_value(ATTR_HOST).encode(),
                    str(source.get_value(ATTR_PORT)).encode(),
                    drive.encode(),
                    path.encode(),
                    cache_path.encode(),
                    task_id.encode(),
                ]
            )
            return True
        else:
            return False

    def clean_task_history(self):
        """Clear all IDLE tasks to maximum set by max_task_history."""
        task_count = 0
        for group in reversed(copy(list(self.attributes.keys()))):
            if group.startswith("T_"):
                if (
                    self.get_value([group, ATTR_STATUS]) == STATUS_IDLE
                    and task_count >= self.max_task_history - 1
                ):
                    self.remove_task(group)
                else:
                    task_count += 1

    def add_task(self, worker_id, request):
        """
        Add new task for Fileserver.

        Each Task is represented by request which is then given to free worker.
        After new task is added task_id is returned back.

        :param worker_id: str
        :param request: list
        :return: str
        """
        self.clean_task_history()
        instruction = request[2]
        task_id = "T_{}".format(next(self.task_counter))
        self.logger.info("Task {} added".format(task_id))

        self.create_attribute(
            ATTR_STATUS, task_id, default_value=STATUS_CONFIGURING, readonly=True
        )
        self.create_attribute(
            ATTR_STARTED_AT,
            task_id,
            default_value=time.time(),
            unit="sec",
            readonly=True,
            default_type=np.float,
        )
        self.create_attribute(
            ATTR_FINISHED_AT, task_id, unit="sec", readonly=True, default_type=np.float
        )
        self.create_attribute(
            ATTR_PROGRESS,
            task_id,
            default_value=0,
            unit="%",
            readonly=True,
            default_type=np.float,
            decimals=2,
        )
        self.create_attribute(
            ATTR_WORKER, task_id, default_value=worker_id, readonly=True
        )
        if instruction == INSTRUCTION_PULL:
            self.create_attribute(
                ATTR_TASK_INSTRUCTION, task_id, default_value="Pull file", readonly=True
            )
            self.create_attribute(
                ATTR_ADDRESS,
                task_id,
                default_value="tcp://{}:{}".format(
                    request[3].decode(), request[4].decode()
                ),
                readonly=True,
            )
            self.create_attribute(
                ATTR_SOURCE_FILE,
                task_id,
                default_value=request[5].decode(),
                readonly=True,
            )
            self.create_attribute(
                ATTR_TARGET_FILE,
                task_id,
                default_value=request[6].decode(),
                readonly=True,
            )
        elif instruction == INSTRUCTION_PUSH:
            self.create_attribute(
                ATTR_TASK_INSTRUCTION, task_id, default_value="Push file", readonly=True
            )
            self.create_attribute(
                ATTR_SOURCE_FILE,
                task_id,
                default_value=request[4].decode(),
                readonly=True,
            )
        elif instruction == INSTRUCTION_FORWARD:
            self.create_attribute(
                ATTR_TASK_INSTRUCTION,
                task_id,
                default_value="Forward file",
                readonly=True,
            )
            self.create_attribute(
                ATTR_SOURCE_FILE,
                task_id,
                default_value=request[3].decode(),
                readonly=True,
            )
        elif instruction == INSTRUCTION_SYNC:
            number_of_files = int(request[3].decode())
            self.create_attribute(
                ATTR_TASK_INSTRUCTION,
                task_id,
                default_value="Sync files",
                readonly=True,
            )
            offset = 4
            syncing_files = []
            for _ in range(number_of_files):
                drive, path = request[offset : offset + 2]
                offset += 2
                syncing_files.append((drive.decode(), path.decode()))
            self.create_attribute(
                ATTR_REQUESTED_FILES,
                task_id,
                default_value=syncing_files,
                readonly=True,
            )
            self.create_attribute(
                ATTR_SYNCED_FILES, task_id, default_value=[], readonly=True
            )
        self.create_attribute(
            ATTR_ABORTED, task_id, default_value=False, default_type=bool, readonly=True
        )
        return task_id

    def remove_task(self, task_id):
        """
        Remove task from list of all tasks.

        :param task_id: str
        """
        if task_id in self.attributes:
            self.logger.info("Task {} removed".format(task_id))
            self.delete_attribute_group(task_id)

    def set_task_progress(self, task_id, progress):
        """
        Set new task progress.

        If syncing multiple files, calculate overall progress based on number of files.
        :param task_id: str
        :param progress: float
        """
        if self.get_value([task_id, ATTR_TASK_INSTRUCTION]) == "Sync files":
            requested_files = len(self.get_value([task_id, ATTR_REQUESTED_FILES]))
            synced_files = len(self.get_value([task_id, ATTR_SYNCED_FILES]).keys())
            sync_file_progress_part = 100 / requested_files
            progress = sync_file_progress_part * synced_files + (
                sync_file_progress_part * (progress / 100)
            )

        self.set_value([task_id, ATTR_PROGRESS], progress)

    def set_task_status(self, task_id, status):
        """
        Set new task status.

        :param task_id: str
        :param status: str
        """
        self.set_value([task_id, ATTR_STATUS], status)

    def abort_task(self, task_id):
        """
        Task was aborted for any reason.

        :param task_id:
        """
        self.logger.info("Task {} aborted".format(task_id))
        self.set_value([task_id, ATTR_ABORTED], True)
        self.set_task_status(task_id, STATUS_IDLE)

    @expose_method({"task_id": "Task id"})
    def stop_task(self, task_id):
        """
        Initiate task to be stopped, based on task_id.

        :param task_id: str
        """
        if task_id not in self.attributes:
            raise DeviceError("Task '{}' does not exists".format(task_id))
        elif self.get_value([task_id, ATTR_STATUS]) != STATUS_BUSY:
            raise DeviceError("Task '{}' is not running".format(task_id))
        self.backend_connector.send_multipart([MSG_ABORT, task_id.encode()])
        self.backend_connector.recv_multipart()

    @expose_method()
    def stop_all_tasks(self):
        """Stop all running Tasks."""
        self.logger.info("Stop all tasks")
        for group in self.attributes:
            if (
                group == "General"
                or self.get_value([group, ATTR_STATUS]) != STATUS_BUSY
            ):
                continue
            self.stop_task(group)

    def stop(self):
        """Stop Fileserver."""
        for worker in self.local_workers:
            self.socket_backend.send_multipart([worker.id, MSG_EMPTY, MSG_TERMINATE])

        self.local_workers = []
        self.running = False

    def close(self):
        self.stop()
        Device.close(self)
