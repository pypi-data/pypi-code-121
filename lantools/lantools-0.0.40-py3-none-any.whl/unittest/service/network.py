from telnetlib import Telnet
import time

def is_alive(host, port):
    try:
        tn = Telnet()
        tn.open(host, port)
        return True
    except ConnectionRefusedError as e:
        return False

def wait_for_ready(host, port):
    for i in range(10):
        if is_alive(host, port):
            time.sleep(1)
            break
        else:
            time.sleep(1)