#  Copyright 2022 Data Spree GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio
import json
import logging.handlers
import os
import signal
import socket
import subprocess
import sys
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional, Dict, AsyncIterator, List

import aiofiles
import aiohttp
import aiohttp_cors
import requests
from aiohttp import web

major_version = sys.version_info.major
minor_version = sys.version_info.minor
if major_version == 3 and minor_version == 7:
    from asyncio.futures import TimeoutError as AioTimeoutError
elif major_version == 3 and minor_version >= 8:
    from asyncio.exceptions import TimeoutError as AioTimeoutError

from dataspree.platform_sdk.client import Client

logger = logging.getLogger(__name__)


class SetupException(Exception):
    pass


class Worker:

    def __init__(self, model_id=None, keep_up=False, keep_up_time=300.0,
                 message_wait_timeout=10.0, send_queue_max_size=10, host='0.0.0.0', port=6714,
                 debug: bool = False):
        """
        :param debug: If true, assertions and __debug__ statements are executed in spawned training process.
        """
        super().__init__()

        self.model_id: int = model_id
        self.keep_up: bool = keep_up
        self.keep_up_time: float = keep_up_time  # seconds
        self.message_wait_timeout = message_wait_timeout  # seconds
        self.debug: bool = debug

        self.status = 'starting'
        self.ready_states = ['idle', 'running']

        self.config = {}
        dataspree_dir = Client.dataspree_dir()
        self.config_file = os.path.join(dataspree_dir, 'training', 'worker.json')

        self.client: Optional[Client] = None

        self.last_model_status_update: int = 0
        self.last_model_status: Optional[Dict] = None
        self.start_iteration: Optional[int] = None

        # self.current_run: Optional[Awaitable] = None
        self.current_job: Optional[Dict] = None
        self.stop_received: bool = False
        self.model_exception: Optional[str] = None

        self.ws = None
        self.send_queue = asyncio.Queue(maxsize=send_queue_max_size)
        # self.message_waiter: Optional[Future] = None
        self.running = True
        self.pool = ThreadPoolExecutor(max_workers=2)
        self.pool_pcom = ThreadPoolExecutor(max_workers=2)

        self.pause = False

        self.host = host
        self.port = port
        self.webapp = web.Application()
        self.site: Optional[web.TCPSite] = None
        cors = aiohttp_cors.setup(self.webapp, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        self.webapp.add_routes([web.get('/status', self.handle_get_status),
                                web.get('/pause', self.handle_get_pause),
                                web.get('/resume', self.handle_get_resume),
                                web.post('/model_status', self.handle_post_model_status),
                                web.post('/setup', self.handle_post_setup)])
        for route in list(self.webapp.router.routes()):
            cors.add(route)

    async def save_config(self):
        async with aiofiles.open(self.config_file, 'wb') as f:
            await f.write(json.dumps(self.config, indent=2).encode('utf-8'))

    @staticmethod
    def get_api_url(platform_host):
        if platform_host == 'api.vision.data-spree.com':
            return f'https://{platform_host}/api'
        return f'http://{platform_host}/api'

    @staticmethod
    def get_ws_url(platform_host):
        if platform_host == 'api.vision.data-spree.com':
            return f'wss://{platform_host}/ws'
        return f'ws://{platform_host}/ws'

    def run(self):
        """
        Start the processing loops.
        """
        loop = asyncio.get_event_loop()
        if loop is None:
            loop = asyncio.new_event_loop()

        # load configuration if exists
        if os.path.exists(self.config_file):
            with open(self.config_file, mode='r') as f:
                self.config = json.loads(f.read())
        else:
            with open(self.config_file, mode='w') as f:
                f.write(json.dumps({}))

        username = self.config.get('username')
        password = self.config.get('password')
        auth_token = self.config.get('auth_token')
        platform_host = self.config.get('platform_host')
        worker_id = self.config.get('worker_id')

        api_url = self.get_api_url(platform_host)
        ws_url = self.get_ws_url(platform_host)

        if ((username is not None and password is not None) or auth_token is not None) and \
                platform_host is not None and worker_id is not None:

            verify_ssl = platform_host == 'api.vision.data-spree.com'
            verify_s3_ssl = verify_ssl

            self.client = Client(username=username, password=password, auth_token=auth_token,
                                 server_url=api_url, verify_ssl=verify_ssl, verify_s3_ssl=verify_s3_ssl)
            # test the connection:
            if self.check_connection():
                self.status = 'idle'
            else:
                self.status = 'connection_error'
        else:
            self.status = 'uninitialized'

        # start internal webserver
        loop.run_until_complete(self.start_webserver())

        # start processing loop
        loop.run_until_complete(
            asyncio.gather(self.run_process_messages(), self.run_send_messages(), self.run_process_jobs()))

    def check_connection(self, worker_id=None, client=None):
        if worker_id is None:
            worker_id = self.config.get('worker_id')
        if client is None:
            client = self.client
        if worker_id is None or client is None:
            return False
        return client.get_jobs(worker_id) is not None

    def status_dict(self):
        return {
            'status': self.status,
            'model_status': self.last_model_status,
            'job': self.current_job
        }

    async def handle_get_status(self, request):
        return web.Response(text=json.dumps(self.status_dict()))

    async def handle_get_pause(self, request):
        self.pause = True
        self.stop_received = True
        return web.Response(status=200)

    async def handle_get_resume(self, request):
        self.pause = False
        return web.Response(status=200)

    async def handle_post_model_status(self, request: web.Request):
        try:
            status = await request.json()
        except Exception as e:
            logger.warning(f'could not parse json message for endpoint /model_status: {e}')
            return web.Response(status=400)

        self.last_model_status_update = time.time()
        self.last_model_status = status

        if status.get('status') == 'exception':
            self.model_exception = status.get('error', 'An error occurred during training.')

        return web.Response(status=200)

    async def handle_post_setup(self, request: web.Request):
        loop = asyncio.get_event_loop()

        config = None
        try:
            config = await request.json()
        except Exception as e:
            logger.warning(f'could not parse json message for endpoint /setup: {e}')

        try:
            if config is None:
                raise SetupException('could not parse setup data')

            # stop the current job
            self.stop_received = True

            client = None

            platform_host = config.get('platform_host')
            if platform_host is None:
                if self.config.get('platform_host') is None:
                    platform_host = 'api.vision.data-spree.com'
                else:
                    platform_host = self.config.get('platform_host')

            api_url = self.get_api_url(platform_host)

            dataset_dir = config.get('dataset_dir')
            if dataset_dir is None and self.config.get('dataset_dir') is not None:
                dataset_dir = config.get('dataset_dir')

            if dataset_dir == '':
                raise SetupException('dataset directory must be specified')
            if not os.path.exists(dataset_dir):
                raise SetupException('dataset directory does not exist')
            if not os.path.isdir(dataset_dir):
                raise SetupException('dataset directory path is not a directory')

            auth_token = config.get('auth_token')
            username = config.get('username')
            password = config.get('password')
            worker_name = config.get('worker_name')

            verify_ssl = platform_host == 'api.vision.data-spree.com'
            verify_s3_ssl = verify_ssl

            new_config = {}
            if auth_token is not None:
                client = Client(auth_token=auth_token, server_url=api_url, verify_ssl=verify_ssl,
                                verify_s3_ssl=verify_s3_ssl)
                new_config['worker_name'] = worker_name
                new_config['auth_token'] = auth_token
                new_config['username'] = None
                new_config['password'] = None
                new_config['platform_host'] = platform_host
                new_config['dataset_dir'] = dataset_dir
            elif username is not None and password is not None:
                client = Client(username=username, password=password, server_url=api_url,
                                verify_ssl=verify_ssl,
                                verify_s3_ssl=verify_s3_ssl)
                new_config['worker_name'] = worker_name
                new_config['username'] = username
                new_config['password'] = password
                new_config['auth_token'] = None
                new_config['platform_host'] = platform_host
                new_config['dataset_dir'] = dataset_dir

            if client is None:
                raise SetupException('could not initialize client')

            if worker_name is None or worker_name == '':
                worker_name = socket.gethostname()
            try:
                new_worker = await loop.run_in_executor(self.pool, client.create_worker, worker_name)
            except requests.exceptions.RequestException as e:
                err_msg = f'could not create worker at {client.server_url}'
                try:
                    response_content = e.response.json()
                    err_msg = f'could not create worker at {client.server_url}: {response_content["error"]}'
                except Exception:
                    pass
                raise SetupException(err_msg)
            new_config['worker_id'] = new_worker['id']
            if not self.check_connection(worker_id=new_worker['id'], client=client):
                raise SetupException('connection check failed')
            # update config
            self.config = new_config

            # close previous websocket connection
            if self.ws is not None:
                try:
                    await self.ws.close()
                except Exception as e:
                    pass

            # set new platform client
            self.client = client

            # write config to file
            await self.save_config()

            self.status = 'idle'
            return web.Response(status=200, body=json.dumps(new_worker))
        except SetupException as e:
            error_msg = str(e)
            return web.Response(status=400, text=error_msg)
        except Exception as e:
            error_msg = 'an unknown exception occurred'
            logger.error(e)
            return web.Response(status=500, text=error_msg)

    async def stop_webserver(self) -> None:
        if self.site is not None:
            await self.site.stop()

    async def start_webserver(self) -> None:
        """
        HTTP server as interface between worker and cli/user interface.
        """
        # web.run_app(self.webapp, host=self.host, port=self.port)
        runner = web.AppRunner(self.webapp)
        await runner.setup()
        self.site = web.TCPSite(runner, self.host, self.port, reuse_address=True)
        try:
            await self.site.start()
        except OSError as e:
            logger.error(f'Could not start internal HTTP server: {e}')
            self.stop_received = True
            self.running = False

    async def run_process_jobs(self) -> None:
        """
        Fetch jobs from the platform and start the model training / evaluation.
        """

        loop = asyncio.get_event_loop()

        job_time = time.time()

        counter = 0
        while self.running:
            counter += 1

            if self.status not in self.ready_states:
                if counter == 1:
                    logger.info('Waiting to get ready')

                if self.status == 'connection_error':
                    # check if the connection is still erroneous
                    if await loop.run_in_executor(self.pool, self.check_connection):
                        self.status = 'idle'
                    else:
                        self.status = 'connection_error'
                        await asyncio.sleep(4.5)
                else:
                    await asyncio.sleep(0.5)

                continue

            if self.pause:
                logger.info('Paused. Waiting to resume')
                await asyncio.sleep(0.5)
                continue

            jobs = await loop.run_in_executor(self.pool, self.client.get_jobs, self.config['worker_id'])
            if jobs is None:
                self.status = 'connection_error'
                continue

            self.current_job = next((job for job in jobs if job['status'] != 'exception'), None)
            if self.current_job is None:
                logger.info('No jobs found')
                message = {
                    'type': 'status',
                    'status': 'idle'
                }
                try:
                    self.send_queue.put_nowait(message)
                except asyncio.QueueFull as e:
                    logger.warning('Websocket sending queue is full.')
                await asyncio.sleep(2)
            else:
                message = {
                    'type': 'status',
                    'status': 'idle'
                }
                try:
                    self.send_queue.put_nowait(message)
                except asyncio.QueueFull as e:
                    logger.warning('Websocket sending queue is full.')

                self.model_exception = None

                server_url: str = self.get_api_url(self.config.get('platform_host'))
                dataset_dir: str = self.config.get('dataset_dir')

                args: List[str]
                if self.debug:
                    args = [sys.executable, '-m', 'dataspree.platform_sdk.base_model']
                else:
                    args = [sys.executable, '-O', '-m', 'dataspree.platform_sdk.base_model']

                model_env = os.environ.copy()
                model_env['DS_JOB_ID'] = str(self.current_job.get('id'))
                model_env['DS_SERVER_URL'] = server_url
                model_env['DS_DATASET_DIR'] = dataset_dir
                model_env['DS_MODEL_CLASS'] = os.environ.get('DS_MODEL_CLASS',
                                                             'dldstraining.trainer_model.TrainerModel')

                username = self.config.get('username')
                password = self.config.get('password')
                token = self.config.get('auth_token')
                if token is not None:
                    model_env['DS_TOKEN'] = token
                else:
                    model_env['DS_USERNAME'] = username
                    model_env['DS_PASSWORD'] = password

                logger.info(f'Start job {self.current_job["id"]}.')

                # set the current job status to running
                await loop.run_in_executor(self.pool, self.client.update_job,
                                           {'id': self.current_job['id'], 'status': 'running'})

                # create subprocess for the model execution
                with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=model_env,
                                      creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)) as process:
                    self.stop_received = False
                    self.status = 'running'

                    process_start_time = time.time()

                    # wait this time before requiring the model status heartbeat
                    process_initial_delay = 240
                    required_heartbeat_interval = 60

                    def read_stdout():

                        trainer_log_file: str = os.path.join(Client.dataspree_temp_dir('trainer_log'), 'log.txt')

                        with open(trainer_log_file, 'a') as log_out_file:
                            log_out_file.write(f'\nLaunch training {self.current_job["id"]}\n')

                        line = None
                        try:
                            while process.poll() is None and line != '':
                                line = process.stdout.readline()
                                line = line.decode('utf-8')
                                sys.stdout.write(line)
                                sys.stdout.flush()

                                # This is a bit slow, but I think it should not affect the performance of the training.
                                # This way don't have corrupt files.
                                try:
                                    with open(trainer_log_file, 'a') as log_out_file:
                                        log_out_file.write(line[:-1])

                                except Exception as e:
                                    logger.info(f'Could not write output "{line}" to log output file: {e}.')

                        except Exception as e:
                            logger.error(f'An exception occurred while trying to communicate with child process: {e}.'
                                         f'Stop listening to the process.')

                    read_stdout_loop = loop.run_in_executor(self.pool_pcom, read_stdout)

                    def send_stop_signal():
                        if hasattr(signal, 'CTRL_BREAK_EVENT'):
                            process.send_signal(signal.CTRL_BREAK_EVENT)
                        else:
                            process.send_signal(signal.SIGINT)

                    def stop_process(terminate_after=900.0):
                        logger.info('Stopping training process...')

                        send_stop_signal()

                        # process.terminate()
                        stop_time = time.time()
                        while process.poll() is None:
                            logger.info('Waiting that the process closes')
                            if time.time() > stop_time + terminate_after:
                                # terminate the process in case it is not stopped after `terminate_after` seconds
                                logger.info('Terminate training process.')
                                process.terminate()
                            time.sleep(3.0)

                    last_model_status_sent = 0
                    # send the training status to the platform at most every 2 seconds
                    training_status_update_interval = 2.0
                    soft_stop_time = None
                    while self.running and process.poll() is None:
                        if self.stop_received:
                            if soft_stop_time is None:
                                await loop.run_in_executor(self.pool_pcom, send_stop_signal)
                                soft_stop_time = time.time()
                            else:
                                logger.info('Waiting that the process closes after soft stop')
                                if time.time() > soft_stop_time + 900.0:
                                    logger.info('Terminate training process.')
                                    process.terminate()
                                await asyncio.sleep(3.0)
                            # await loop.run_in_executor(self.pool_pcom, stop_process, 900.0)

                        # check if the model is live
                        now = time.time()
                        if now > process_start_time + process_initial_delay and \
                                now > self.last_model_status_update + required_heartbeat_interval:
                            # the model is assumed to be not running anymore in case the heartbeat was not received
                            # for `required_heartbeat_interval` seconds and the process will be stopped
                            logger.warning(f'No heartbeat received for at least {required_heartbeat_interval:.1f}s.')
                            await loop.run_in_executor(self.pool_pcom, stop_process, 30.0)

                        if self.last_model_status is not None and \
                                self.last_model_status_update > last_model_status_sent + training_status_update_interval:

                            # set the start iteration of the job if this was not yet done
                            if self.start_iteration is None:
                                start_iteration = self.last_model_status.get('start_iteration')
                                if start_iteration is not None:
                                    updated_job = {
                                        'id': self.current_job['id'],
                                        'start_iteration': start_iteration
                                    }
                                    await loop.run_in_executor(self.pool, self.client.update_job, updated_job)
                                    self.start_iteration = start_iteration

                            last_model_status_sent = self.last_model_status_update
                            message = {
                                'type': 'status',
                                'status': self.last_model_status.get('status', 'running'),
                                'iteration': self.last_model_status.get('iteration'),
                                'start_iteration': self.last_model_status.get('start_iteration'),
                                'end_iteration': self.last_model_status.get('end_iteration'),
                                'epoch': self.last_model_status.get('epoch'),
                                'eta': self.last_model_status.get('eta'),
                                'error': self.last_model_status.get('error'),
                                'job': self.current_job,
                                'sub_status': self.last_model_status.get('task'),
                                'sub_status_info': self.last_model_status.get('task_info'),
                            }

                            information = ', '.join((f'{k}={v}' for k, v in self.last_model_status.items()))
                            logger.debug(f'Iteration callback (job: {self.current_job}, information: {information})')
                            try:
                                self.send_queue.put_nowait(message)
                            except asyncio.QueueFull as e:
                                logger.warning('Websocket sending queue is full.')

                        await asyncio.sleep(0.5)

                    read_stdout_loop.cancel()

                logger.info('Training process stopped.')

                if process.returncode != 0:
                    logger.warning('Model training failed.')
                    if self.model_exception is None:
                        self.model_exception = 'an error occurred'

                if self.model_exception is not None:
                    updated_job = {
                        'id': self.current_job['id'],
                        'status': 'exception',
                        'details': json.dumps({
                            'error': self.model_exception,
                        })
                    }
                    await loop.run_in_executor(self.pool, self.client.update_job, updated_job)
                elif self.last_model_status is not None:
                    message = {
                        'type': 'status',
                        'status': 'stopped',
                        'iteration': self.last_model_status.get('iteration', 0),
                        'job': self.current_job,
                    }
                    await self.send_message(message)
                    await loop.run_in_executor(self.pool, self.client.delete_job, self.current_job.get('id'))

                # reset the job time so that the worker can execute some more jobs
                job_time = time.time()

                self.status = 'idle'
                self.last_model_status = None
                self.start_iteration = None

            if not self.keep_up:
                now = time.time()
                if now - job_time > self.keep_up_time:
                    self.stop_received = True
                    self.running = False
                    await self.stop_webserver()

    async def run_send_messages(self) -> None:
        """
        Send enqueued messages via websocket.
        """
        while self.running:
            try:
                message = await asyncio.wait_for(self.send_queue.get(), timeout=1.0)
                await self.send_message(message)
            except AioTimeoutError as e:
                pass

    async def run_process_messages(self) -> None:
        """
        Process incoming websocket messages and check the job that is currently running.
        """
        loop = asyncio.get_event_loop()

        while self.running and self.status not in self.ready_states:
            await asyncio.sleep(0.1)

        websocket_connection = self.websocket_connection()

        while self.running:
            # try to fetch a message from the websocket connection
            message: Optional[Dict] = None
            try:
                message = await asyncio.wait_for(websocket_connection.__anext__(), timeout=self.message_wait_timeout)
            except StopAsyncIteration as e:
                websocket_connection = self.websocket_connection()
                await asyncio.sleep(0.5)
                continue
            except AioTimeoutError as e:
                pass
            except Exception as e:
                logger.exception(f'Exception during fetching websocket messages: {e}')

            # fetch job information from the platform
            if message is None:
                if self.current_job is not None and not self.stop_received:
                    job = await loop.run_in_executor(self.pool, self.client.get_job, self.current_job.get('id'))
                    if job is None:
                        message = {
                            'type': 'job_deleted',
                            'job_id': self.current_job.get('id')
                        }

            if message is not None:
                if message.get('type', '') == 'job_deleted' and \
                        self.current_job is not None and message.get('job_id') == self.current_job.get('id'):
                    self.stop_received = True

                # if self.message_waiter is not None:
                #     if not self.message_waiter.done():
                #         self.message_waiter.set_result(None)

    async def websocket_connection(self) -> AsyncIterator[Dict]:
        """
        Create a websocket connection to the worker websocket API to receive notifications about new jobs, deleted jobs
        etc., and to send status messages to the platform, e.g. after an iteration completed.
        :return: Iterator for incoming messages.
        """
        while self.running:
            # connect via websocket to the platform
            try:
                async with aiohttp.ClientSession() as session:
                    platform_host = self.config.get('platform_host')
                    username = self.config.get('username')
                    password = self.config.get('password')
                    auth_token = self.config.get('auth_token')
                    worker_id = self.config['worker_id']
                    api_url = self.get_api_url(platform_host)
                    auth_data = dict(remember_me=True)
                    if username is not None and password is not None:
                        auth_data['username'] = username
                        auth_data['password'] = password
                    elif auth_token is not None:
                        auth_data['token'] = auth_token
                    else:
                        raise Exception('No authentication credentials provided.')
                    async with session.post(f'{api_url}/auth/users/login/', data=auth_data) as resp:
                        if resp.status != 200:
                            logger.error('Could not log in to AI platform. Retry soon.')
                            await asyncio.sleep(8)
                            continue

                    ws_url = self.get_ws_url(platform_host)
                    worker_url = '{}/worker/{}'.format(ws_url, worker_id)
                    logger.debug(f'Try to connect via websocket to {worker_url}')
                    async with session.ws_connect(worker_url) as ws:
                        logger.debug(f'Websocket connection established to {worker_url}')
                        self.ws = ws
                        async for msg in ws:
                            logger.debug(f'Received message via websockets: {msg.data}')
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                message_dict = json.loads(msg.data)
                                yield message_dict
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logger.warning('Websocket connection error.')
                                break

                    self.ws = None
            except aiohttp.ClientError:
                pass

            # wait 2 seconds before trying to re-connect
            await asyncio.sleep(2)

    async def send_message(self, message: Dict) -> None:
        """
        Send a message via websockets to the platform.
        :param message: Dictionary to be serialized as json.
        """
        if self.ws:
            try:
                await self.ws.send_str(json.dumps(message))
            except ConnectionResetError:
                pass
            except Exception as e:
                logger.warning(e)

    def stop(self) -> None:
        """
        Stop the worker.
        """
        self.stop_received = True
        self.running = False

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.stop_webserver())

    @staticmethod
    def start(model_id=None, keep_up=False, keep_up_time=900.0,
              message_wait_timeout=30.0, send_queue_max_size=10, host='0.0.0.0', port=6714, debug: bool = False):
        worker = None
        try:
            logger.info('Creating worker...')
            worker = Worker(model_id, keep_up, keep_up_time, message_wait_timeout, send_queue_max_size, host, port,
                            debug=debug)
            logger.info('Starting worker...')
            worker.run()
        except KeyboardInterrupt:
            logger.info('Stopping worker...')
            if worker is not None:
                worker.stop()
            raise KeyboardInterrupt
        except Exception as e:
            logging.error(f'Unknown exception during worker execution: {e}')

            if __debug__:
                raise e from None

            if worker is not None:
                worker.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-6s %(message)s')
    Worker.start()
