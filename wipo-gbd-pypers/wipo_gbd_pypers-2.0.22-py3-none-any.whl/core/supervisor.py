import json
import time
import uuid
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pypers.utils.filelock import FileLock


manager = None


def get_status_manager(supervised=True):
    global manager
    if not manager:
        manager = StatusManager(supervised)
    return manager


class SupervisorServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        endpoints = {
            '/healthcheck': self.sanity,
            '/status': self.status,
            '/kill': self.kill
        }
        if self.path in endpoints.keys():
            endpoints[self.path]()
        else:
            self.send_error(404)

    def kill(self):
        try:
            os.getcwd()
            if get_status_manager().is_busy():
                self._send_message(400, {'service': 'running'})
                return
        except Exception as e:
            pass
        self._send_message(200, {'service': 'stop'})
        get_status_manager().stop()

    def sanity(self):
        if get_status_manager().is_running():
            try:
                os.getcwd()
                self._send_message(200, {'service': 'running'})
            except Exception as e:
                self._send_message(200, {'service': 'failed', 'error': 'Lost pointer to filesystem'})

        else:
            self._send_message(503, {'service': 'failed'})

    def _send_message(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(payload), "utf-8"))

    def status(self):
        try:
            os.getcwd()
        except Exception as e:
            self._send_message(200, {'service': 'failed', 'error': 'Lost pointer to filesystem'})
        if get_status_manager().is_busy():
            self._send_message(200, {'status': 'busy'})
        else:
            self._send_message(200, {'status': 'idle'})


class StatusManager:

    STATUS_LOCK = 'status'
    RUNNING_LOCK = 'running'
    KILLED = False
    TIMEOUT = 30  # in seconds

    def __init__(self, supervised):
        self.supervised = supervised
        container_id =  os.environ.get("ECS_CONTAINER_METADATA_URI", None)
        if container_id:
            container_id = container_id.split('/')[-1]
        else:
            container_id = str(uuid.uuid1())
        self.path = os.path.join(os.getcwd(), container_id)
        os.makedirs(self.path, exist_ok=True)
        self.cleanup()

    def keep_alive(self):
        return not self.KILLED

    def stop(self):
        self.KILLED = True
        self.cleanup()

    def cleanup(self):
        try:
            os.remove(os.path.join(self.path, self.STATUS_LOCK))
        except FileNotFoundError as e:
            pass
        try:
            os.remove(os.path.join(self.path, self.RUNNING_LOCK))
        except FileNotFoundError as e:
            pass

    def set_status(self, busy=False):
        if not self.supervised:
            return
        with FileLock(self.path, self.STATUS_LOCK):
            with open(os.path.join(self.path, self.STATUS_LOCK), 'w') as f:
                f.write('busy' if busy else 'idle')

    def set_sanity(self):
        if not self.supervised:
            return
        with FileLock(self.path, self.RUNNING_LOCK):
            with open(os.path.join(self.path, self.RUNNING_LOCK), 'w') as f:
                f.write("%s" % time.time())

    def is_running(self):
        if not self.supervised:
            return False
        if self.is_busy():
            return True
        with FileLock(self.path, self.RUNNING_LOCK):
            with open(os.path.join(self.path, self.RUNNING_LOCK), 'r') as f:
                last_ping = float(f.read())
                if time.time() - last_ping < self.TIMEOUT:
                    return True
            return False

    def is_busy(self):
        if not self.supervised:
            return False
        with FileLock(self.path, self.STATUS_LOCK):
            if os.path.exists(os.path.join(self.path, self.STATUS_LOCK)):
                with open(os.path.join(self.path, self.STATUS_LOCK), 'r') as f:
                    status = f.read()
                    return status == 'busy'
            return False


class SupervisorServer:
    def __init__(self, port):
        self.port = port
        self.hostname = '0.0.0.0'
        self.webserver = HTTPServer((self.hostname, self.port), SupervisorServerHandler)
        self.is_started = False



    def start(self):
        print('Starting supervisor on port %s' % self.port)
        self.is_started = True
        self.webserver.serve_forever()

    def stop(self):
        self.webserver.server_close()
        self.webserver.shutdown()
        print('Server stopped')
