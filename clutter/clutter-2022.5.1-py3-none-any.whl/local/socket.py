import socket


# get local ip address not 127.0.0.1
def get_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
    return ip


# get random available port
def get_free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
    return port
