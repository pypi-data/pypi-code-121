import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import websockets
import ssl

import requests

import pickle

import random
import string
from functools import partial

import time

import logging
logging.getLogger('werkzeug').disabled = True

import os

print_verbose = lambda s: print(f"--CommunicationHandler-- : {s}" )

try:
    from flask import Flask
    from flask import request
    from gevent.pywsgi import WSGIServer
except ImportError:
    logging.debug("flask/gevent not found - only websocket servers can be spawned (\'send\' not affected)")
    pass

class CommunicationHandler():
    def __init__(
            self,
            protocol='websocket',
            cert_path=None,
            num_retry=40,
            retry_interval=15,
            verbose=True,
            max_cache_size=100,
            cache_file_path='/default.cache'
        ):

        self.protocol = protocol
        self.msg_queues = {}
        self.resp_queue = {}
        self.resp_cache = {}

        self.num_retry = num_retry
        self.retry_interval = retry_interval

        self.max_cache_size = 100
        self.cache_file_path = cache_file_path

        self.verbose = verbose

        self.ssl = False
        self.ssl_context = None

        if cert_path is not None:
            self.cert_path = cert_path
            self.ssl = True

            if self.protocol == 'websocket':
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.ssl_context.load_cert_chain(certfile=self.cert_path)

        self.servers = []

        self.load_cache_from_file()

    async def send(self, msg, addr):
        if self.protocol == 'websocket':
            url = f"{('wss' if self.ssl else 'ws')}://{addr}"

            async with websockets.connect(url, max_size=None, max_queue=None, ping_interval=None, ssl=self.ssl_context) as websocket:
                await websocket.send(msg)
                resp = pickle.loads(await websocket.recv())
                return resp

        elif self.protocol == 'http':
            url = f"{'https' if self.ssl else 'http'}://{addr}"

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(2) as pool:
                encoded_resp = await loop.run_in_executor(pool, partial(requests.post, url=url, data=msg, verify=(self.cert_path if self.ssl else True)))
                resp = pickle.loads(encoded_resp.content)
                return resp

    async def send_msg(self, msg, addr, resp_required = True):
        msg_resp = None
        poll_resp_failed = False

        while (msg_resp == None or poll_resp_failed == True):
            # Generate random 16-char id
            id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            encoded_msg = pickle.dumps((id, msg))

            for attempt in range(self.num_retry):
                try:
                    send_resp = await self.send(encoded_msg, addr)
                except:
                    if (attempt == 0):
                        logging.error(f"Cannot connect to {addr} - attempting to connect every {self.retry_interval} seconds (max attempts: {self.num_retry})")
                    if (self.num_retry - attempt > 1):
                        if self.verbose: print_verbose(f'Send attempt {attempt + 1} failed for message {id}')
                        await asyncio.sleep(self.retry_interval)
                        continue
                    else:
                        logging.error(f"Failed to send message after {self.num_retry} attempts")
                        # raise
                else:
                    if (attempt != 0):
                        logging.error(f"Connection to {addr} restored")
                    break

            if self.verbose: print_verbose(f'Message sent: {msg}')

            if (resp_required):
                for attempt in range(self.num_retry):
                    try:
                        msg_resp, poll_resp_failed = await self.poll_msg_resp(addr, id)
                    except:
                        if (attempt == 0):
                            logging.error(f"Cannot connect to {addr} - attempting to connect every {self.retry_interval} seconds (max attempts: {self.num_retry})")
                        if (self.num_retry - attempt > 1):
                            if self.verbose: print_verbose(f'Receive response attempt {attempt + 1} failed for message {id}')
                            await asyncio.sleep(self.retry_interval)
                            continue
                        else:
                            logging.error(f"Failed to receive response after {self.num_retry} attempts")
                            # raise
                    else:
                        if (attempt != 0):
                            logging.error(f"Connection to {addr} restored")
                        if (not poll_resp_failed and self.verbose): print_verbose(f'Response received: {msg_resp}')
                        break
            else:
                msg_resp = send_resp
        
        return msg_resp

    async def poll_msg_resp(self, addr, id):
        encoded_msg = pickle.dumps((id, 'POLL'))

        for attempt in range(self.num_retry):
            if self.verbose: print_verbose(f"Polling for msg {id}")
            msg_resp = await self.send(encoded_msg, addr)
            if (msg_resp != "NOT_FINISHED"):
                return msg_resp, False
            await asyncio.sleep(5)

        logging.error(f"Response to message {id} not found in {self.num_retry} attempts - resending with new id")
        return None, True

    def create_server(self, host, port):
        self.msg_queues[f'{host}:{port}'] = {}

        if self.protocol == 'websocket':
            self.servers.append(WSServerHandler(host, int(port), self))
        else:
            self.servers.append(HTTPServerHandler(host, int(port), self))
        if self.verbose: print_verbose('Server created')

    def _start_ws_servers(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(asyncio.gather(
            *[websockets.serve(s.parse_msg, s.host, s.port, max_size=None, max_queue=None, ping_interval=None, ssl=self.ssl_context) for s in self.servers])
        )
        loop.run_forever()

    def start_servers(self):
        if self.verbose: print_verbose('Servers started')
        if self.protocol == 'websocket':
            self.server_thread = Thread(target=self._start_ws_servers)
            self.server_thread.start()
        elif self.protocol == 'http':
            self.server_threads = [Thread(target=s.start_server) for s in self.servers]
            for th in self.server_threads:
                th.start()

        self.start_resp_cache_cleaner()

    async def get_msg(self, addr):
        while (len(self.msg_queues[addr]) == 0):
            await asyncio.sleep(5)
        if self.verbose: print_verbose(self.msg_queues)

        msg_id = list(self.msg_queues[addr])[0]
        msg_entry = self.msg_queues[addr].pop(msg_id)
        if self.verbose: print_verbose(f"Message {msg_id} popped from queue")

        return msg_entry, msg_id

    def push_msg_resp(self, resp, id):
        self.resp_queue[id] = resp
        if self.verbose: print_verbose(f"Response to message {id} added to queue")

    def start_resp_cache_cleaner(self):
        self.cleaner_thread = Thread(target=self._clean_resp_cache)
        self.cleaner_thread.start()

    def _clean_resp_cache(self):
        while True:
            while (len(self.resp_cache) <= self.max_cache_size):
                time.sleep(3)
            msg_id = list(self.resp_cache)[0]
            if self.verbose: print_verbose(f"Response to message {msg_id} removed from cache")
            self.resp_cache.pop(msg_id)

    def write_cache_to_file(self):
        if not os.path.exists(self.cache_file_path):
            os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
        with open(self.cache_file_path, 'wb') as f:
            pickle.dump(self.resp_cache, f)

    def load_cache_from_file(self):
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, 'rb') as f:
                    self.resp_cache = pickle.load(f)
                    if self.verbose: print_verbose(f"Loaded cache from {self.cache_file_path} - {len(self.resp_cache)} entries found")
            except:
                logging.error(f"Failed to load cached responses from {self.cache_file_path}")

class HTTPServerHandler():
    def __init__(self, host, port, comm_handler):
        self.host = host
        self.port = port

        self.comm_handler = comm_handler

        self.flask_server = Flask(f"CommunicationHandler HTTP Server - {self.port}")
        self.flask_server.logger.disabled = True
        self.flask_server.add_url_rule('/', view_func=self.parse_msg, methods=['POST'])

    def start_server(self):
        # self.flask_server.run(host=self.host, port=self.port, ssl_context=self.ssl_context)
        WSGIServer((self.host, self.port), self.flask_server, log=None).serve_forever()

    def parse_msg(self):
        encoded_msg = request.data
        id, msg = pickle.loads(encoded_msg)

        if msg == 'POLL':
            if id in self.comm_handler.resp_queue:
                resp = pickle.dumps(self.comm_handler.resp_queue[id])
                self.comm_handler.resp_cache[id] = (self.comm_handler.resp_queue[id], time.gmtime())
                self.comm_handler.resp_queue.pop(id)
                self.comm_handler.write_cache_to_file()
                return resp
            elif id in self.comm_handler.resp_cache:
                resp = pickle.dumps(self.comm_handler.resp_cache[id][0])
                return resp
            else:
                return pickle.dumps("NOT_FINISHED")
        else:
            self.comm_handler.msg_queues[f'{self.host}:{self.port}'][id] = msg
            return pickle.dumps("ACK")


class WSServerHandler():
    def __init__(self, host, port, comm_handler):
        self.host = host
        self.port = port

        self.comm_handler = comm_handler

    async def parse_msg(self, websocket, path):
        encoded_msg = await websocket.recv()
        id, msg = pickle.loads(encoded_msg)

        if msg == 'POLL':
            if id in self.comm_handler.resp_queue:
                await websocket.send(pickle.dumps(self.comm_handler.resp_queue[id]))
                self.comm_handler.resp_cache[id] = (self.comm_handler.resp_queue[id], time.gmtime())
                self.comm_handler.resp_queue.pop(id)
                self.comm_handler.write_cache_to_file()
            elif id in self.comm_handler.resp_cache:
                await websocket.send(pickle.dumps(self.comm_handler.resp_cache[id][0]))
            else:
                await websocket.send(pickle.dumps("NOT_FINISHED"))
        else:
            self.comm_handler.msg_queues[f'{self.host}:{self.port}'][id] = msg
            await websocket.send(pickle.dumps("ACK"))