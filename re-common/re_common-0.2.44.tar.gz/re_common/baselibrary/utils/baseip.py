import re
import socket
import time

import requests
from re_common.baselibrary.utils.core.mdeprecated import deprecated


def GetLocalIPByPrefix(prefix):
    """
    多网卡情况下，根据前缀获取IP
    prefix = "192.168"
    """
    localIP = ''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if ip.startswith(prefix):
            localIP = ip
    return localIP


def get_local_ip(ifname='eth0'):
    """
        prefix = enp2s0  or eth0
    :param ifname:
    :return:
    """
    import socket, fcntl, struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15], 'utf-8')))[20:24])




class BaseIp(object):
    def __init__(self):
        self.ocalIP = ''

    @deprecated
    def get_ip(self, proxy=None, count=0):
        """
        获取外网ip
        :return:
        """
        year = str(time.localtime().tm_year)
        url = "http://" + year + ".ip138.com/ic.asp"
        print(url)
        try:
            response = requests.get(url, proxies=proxy, timeout=(30, 60))
            ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", response.content.decode(errors='ignore')).group(0)
            return ip
        except Exception as e:
            print(str(e))
            count += 1
            if count > 2:
                print("出现 错误请检查url是否因年份发生改变")
                return False
            return self.get_ip(proxy, count)

    def GetLocalIPByPrefix(self, prefix):
        """
        # 多网卡情况下，根据前缀获取IP
        :param prefix: 192.168
        :return:
        """
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip.startswith(prefix):
                self.localIP = ip
        return self.localIP


    def work_server(self):
        """
        开启监测访问本机ip的ip
        :return:
        """

        def hello_world_app(environ, start_response):
            status = '200 OK'  # HTTP Status
            headers = [('Content-type', 'text/plain; charset=utf-8')]  # HTTP Headers
            start_response(status, headers)
            msg = 'Hello %s\n' % environ["REMOTE_ADDR"]
            return [msg.encode('utf8')]

        from wsgiref.simple_server import make_server
        with make_server('', 5678, hello_world_app) as httpd:
            print("Serving on port 5678...")
            httpd.serve_forever()
