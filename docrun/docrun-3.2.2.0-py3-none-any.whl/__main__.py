name = "docrun"
import threading
import time
from . import server_kernel
from . import server_ssh

def ssh_loop():
    while True:
        server_ssh.run_server()
        time.sleep(1)
        pass
    pass

def kernel_loop():
    while True:
        server_kernel.run_server()
        time.sleep(1)
        pass
    pass

threading.Thread(target=ssh_loop).start()

threading.Thread(target=kernel_loop).start()


