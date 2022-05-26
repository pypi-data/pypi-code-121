import socket
from sometools.sync_tools.base import Base

class IpMixIn(Base):

    def __init__(self, *args, **kwargs):
        super(IpMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def get_host_ip() -> str:
        """
        获取本机ip地址
        get the local ip address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
