import threading
from multiprocessing import Process
from .network import is_alive, wait_for_ready
import time
import os
import subprocess
import signal

def start_fastapi(entry="index:app", *, host='0.0.0.0', port=8000) -> Process:
    def start_server():
        import uvicorn
        uvicorn.run(entry, host=host, port=port)

    service = Process(target=start_server, args=())
    service.start()
    
    wait_for_ready(host, port)
    return service

class Service:
    def __init__(self, command=["python", "/app/index.py"]):
        self._process = subprocess.Popen(command)

    def wait_for_ready(self, host='0.0.0.0', port=80):
        wait_for_ready(host, port)
        return self

    def terminate(self):
        self._process.send_signal(signal.SIGTERM)
        self._process.wait(20)

