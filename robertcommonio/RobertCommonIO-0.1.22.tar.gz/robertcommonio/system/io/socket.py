import asyncore
import logging
import sys
import socket
from typing import NamedTuple, Any, Optional
from enum import Enum
from threading import Thread, Lock, Event

from robertcommonbasic.basic.cls.utils import daemon_thread
from robertcommonbasic.basic.data.frame import FRAMEFLAG, PACKAGETYPE, FRAMETYPE, TRANSFERTYPE, pack_frame, unpack_frame, get_pack_start_length, get_pack_header_length, convert_bytes_to_int


class SocketType(Enum):
    TCP_CLIENT = 'tcp_client'
    TCP_SERVER = 'tcp_server'
    UDP_CLIENT = 'udp_client'
    UDP_SERVER = 'udp_server'


class SocketConfig(NamedTuple):
    MODE: SocketType
    HOST: str
    PORT: int = 9500
    POOL: int = 0
    BUFFER: int = 50000
    LISTEN: int = 500
    TIME_OUT: int = 5
    CALL_BACK: dict = {}
    HANDLE_CLASS: Any = None
    PARAENT_CLASS: Any = None


# 定制应答式处理类
class SocketHandler(asyncore.dispatcher_with_send):

    def __init__(self, config: SocketConfig, sock=None, addr=None):
        asyncore.dispatcher_with_send.__init__(sock)

        self.config = config
        self.sock = sock
        self.addr = addr
        self.valid = True

        self.start_length = get_pack_start_length()
        self.header_length = get_pack_header_length()

        if self.config.MODE == SocketType.TCP_CLIENT:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((self.config.HOST, self.config.PORT))
        elif self.config.MODE == SocketType.UDP_CLIENT:
            self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.connect((self.config.HOST, self.config.PORT))

    def __str__(self):
        if isinstance(self.addr, tuple) and len(self.addr) >= 2:
            return f"{self.addr[0]}:{self.addr[1]}"
        return str(self.addr)

    def __del__(self):
        self.valid = False
        self.close()

    def format_bytes(self, data: bytes) -> str:
        return ' '.join(["%02X" % x for x in data]).strip()

    def handle_read(self):
        try:
            data_start = self.recv(self.start_length)    # 包头
            if len(data_start) == self.start_length:
                if data_start == FRAMEFLAG.START_FLAG:    #
                    data_header = self.recv(self.header_length)    # 包头长度
                    if len(data_header) == self.header_length:
                        data_end_length = convert_bytes_to_int(data_header[-4:]) + self.start_length + 1
                        data_end = self.recv(data_end_length)  # 包内容
                        if len(data_end) == data_end_length:
                            if data_end[-2:] == FRAMEFLAG.END_FLAG: # 包结尾
                                if 'analyze_data' in self.config.CALL_BACK.keys():
                                    self.config.CALL_BACK['analyze_data'](self, data_start + data_header + data_end)
        except Exception as e:
            logging.error(f"handle read({self}) fail ({e.__str__()})")

    def handle_error(self):
        t, e, trace = sys.exc_info()
        if 'handle_error' in self.config.CALL_BACK.keys():
            self.config.CALL_BACK['handle_error'](self, e)
        self.close()
        self.valid = False

    def handle_close(self):
        if 'handle_close' in self.config.CALL_BACK.keys():
            self.config.CALL_BACK['handle_close'](self)
        self.close()
        self.valid = False

    def handle_connect(self):    
        if 'handle_connect' in self.config.CALL_BACK.keys():
            self.config.CALL_BACK['handle_connect'](self)

    def writable(self):
        return True

    def handle_write(self):
        pass

    def readable(self):
        return True

    def check_invalid(self) -> bool:
        return self.valid


class SocketServer(asyncore.dispatcher):

    def __init__(self, config: SocketConfig):
        asyncore.dispatcher.__init__(self)
        self.config = config
        self.sockets = {}

        if self.config.MODE == SocketType.TCP_SERVER:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.set_reuse_addr()
        self.bind((self.config.HOST, self.config.PORT))

        if self.config.MODE == SocketType.TCP_SERVER:
            self.listen(self.config.LISTEN)

    def handle_close(self):
        self.close()

    def handle_accept(self):
        client = self.accept()
        if client is not None:
            sock, addr = client
            if self.verify_request(sock, addr) is True:
                if self.config.HANDLE_CLASS is not None:
                    self.config.HANDLE_CLASS(self.config, sock, addr, self)
                else:
                    self.sockets[f"{addr[0]}:{addr[1]}"] = SocketHandler(self.config, sock, addr)

    def verify_request(self, sock, address):
        return True

    def clear_invalid(self):
        sock_addrs = list(self.sockets.keys())

        for sock_addr in sock_addrs:
            if sock_addr in self.sockets.keys() and self.sockets[sock_addr].check_invalid() is False:
                del self.sockets[sock_addr]


class SocketAccessor:

    def __init__(self, config: SocketConfig):
        self.config = config
        self.accessor = None
        self.thread = None

    def __del__(self):
        self.exit()

    def exit(self):
        if self.accessor:
            self.accessor.close()
        if self.thread:
            self.thread.join()
        self.accessor = None
        self.thread = None

    def start(self, thread: bool = True):
        if self.config.MODE in [SocketType.TCP_SERVER, SocketType.UDP_SERVER]:
            self.accessor = SocketServer(self.config)
        else:
            if self.config.HANDLE_CLASS is not None:
                self.accessor = self.config.HANDLE_CLASS(self.config)
            else:
                self.accessor = SocketHandler(self.config)

        if self.config.POOL == 0:
            if thread is True:
                self.thread = Thread(target=asyncore.loop)
            else:
                asyncore.loop()
        else:
            if thread is True:
                self.thread = Thread(target=asyncore.loop, kwargs = {'timeout': self.config.TIME_OUT})
            else:
                asyncore.loop(self.config.TIME_OUT)

        if thread is True and self.thread:
            self.thread.start()


#####
class AsyncResult():

    def __init__(self, client, request_id: int, data: bytes, timeout: float, retries: int = 1):
        self.client = client
        self.request_id = request_id
        self.data = data
        self.retries = retries
        self.timeout = timeout
        self.wait_event = Event()
        self.error = None
        self.result = None

    def __del__(self):
        self.close()

    def close(self):
        self.wait_event.clear()

    def send_request(self, wait_config: bool = True) -> dict:
        for r in range(self.retries):
            self.send()
            if wait_config is False:
                if self.error:
                    raise self.error
                return {}
            else:
                if self.wait(self.timeout) is True:
                    return self.result
        if self.error:
            raise self.error
        raise Exception(f"no config")

    def recv(self, package: dict):
        if package.get('package_index') == self.request_id:
            self.wait_event.set()
        self.result = package

    def format_bytes(self, data: bytes) -> str:
        return ' '.join(["%02X" % x for x in data]).strip()

    def send(self):
        self.error = None
        try:
            if self.client:
                if self.client.send(self.data) <= 0:
                    raise Exception(f"send fail")
            else:
                raise Exception(f"no connect")
        except Exception as e:
            self.error = Exception(f"send exception({e.__str__()})")

    def wait(self, timeout: float) -> bool:
        while True:
            if not self.wait_event.wait(timeout):
                return False
            return True


class AsyncResultManage():
    
    def __init__(self, start_package_id: int, end_package_id: int, call_backs: dict):
        self.start_package_id = start_package_id
        self.end_package_id = end_package_id
        self.call_backs = call_backs
        
        self.package_id = start_package_id
        self.requests = {}
        
    def set_debug_log(self, content: str):
        if 'set_debug_log' in self.call_backs.keys():
            self.call_backs['set_debug_log'](content)

    def get_pack_id(self) -> int:
        if self.package_id >= self.end_package_id:
            self.package_id = self.start_package_id
        self.package_id = self.package_id + 1
        return self.package_id

    def config_request(self, request_id: int, result: dict = None):
        if request_id in self.requests.keys():
            if result is not None:
                self.set_debug_log(f"recv {request_id} (FRAMETYPE.CONFIG)")
                self.requests[request_id].recv(result)
            else:
                del self.requests[request_id] 
    
    def create_config(self, client, package_type: int, package_index: int, transfer_type: int, data: Any):
        self.set_debug_log(f"send {package_index}({FRAMETYPE(FRAMETYPE.CONFIG).__str__()}--{PACKAGETYPE(package_type).__str__()}--{TRANSFERTYPE(transfer_type).__str__()})")
        answer = {}
        answer['frame_type'] = FRAMETYPE.CONFIG
        answer['package_type'] = package_type
        answer['package_index'] = package_index
        answer['transfer_type'] = transfer_type
        answer['data'] = data
        return client.send(pack_frame(answer))

    def create_request(self, client, package_index: Optional[int], frame_type: int, package_type: int, transfer_type: int, data, timeout: float, retries: int = 1, wait_config: bool = True):
        try:
            if package_index is None:
                package_index = self.get_pack_id()
            self.set_debug_log(f"send {package_index}({FRAMETYPE(frame_type).__str__()}--{PACKAGETYPE(package_type).__str__()}--{TRANSFERTYPE(transfer_type).__str__()})")
            self.requests[package_index] = AsyncResult(client, package_index, pack_frame({'frame_type': frame_type, 'package_type': package_type, 'package_index': package_index, 'transfer_type': transfer_type, 'data': data}), timeout, retries)
            return self.requests[package_index].send_request(wait_config)
        except Exception as e:
            logging.error(f"create_request({client})({e.__str__()})")
        finally:
            self.config_request(package_index)


class SocketIPHandler():

    def __init__(self, config: SocketConfig, sock=None, addr=None):
        self.config = config
        self.sock = sock
        self.addr = addr
        self.reg_tag = ''
        self.valid = True
        self.lock = Lock()

        self.start_length = get_pack_start_length()
        self.header_length = get_pack_header_length()
        self.exit_flag = False
        self.rec_buffer = b''

        self.receive().start()
        
        #触发连接事件
        self.handle_connect()

    def __str__(self):
        if isinstance(self.addr, tuple) and len(self.addr) >= 2:
            return f"{self.addr[0]}:{self.addr[1]}"
        return str(self.addr)

    def __del__(self):
        self.close()

    def format_bytes(self, data: bytes) -> str:
        return ' '.join(["%02X" % x for x in data]).strip()

    def close(self):
        self.valid = False
        self.exit_flag = True
        if self.sock:
            self.sock.close()
        self.sock = None

    def handle_connect(self):
        if 'handle_connect' in self.config.CALL_BACK.keys():
            self.config.CALL_BACK['handle_connect'](self)

    def handle_close(self, reason: str=''):
        self.close()
        if 'handle_close' in self.config.CALL_BACK.keys():
            self.config.CALL_BACK['handle_close'](self, reason)

    def handle_error(self, e: Exception):
        self.close()
        if 'handle_error' in self.config.CALL_BACK.keys():
            self.config.CALL_BACK['handle_error'](self, e)
        else:
            logging.error(f"handle_error({self})({e.__str__()})")
            
    def recv_bytes(self, length: int) -> Optional[bytes]:
        data = b''
        buffer = self.config.BUFFER
        group = int(length / buffer)
        for i in range(group):
            data += self.sock.recv(buffer)
        if len(data) < length:
            data += self.sock.recv(length - len(data))
        if data is None or len(data) == 0:
            self.handle_close(f"remote close")
        elif len(data) != length:
            return None
        return data

    def recv_default(self):
        data_start = self.recv_bytes(self.start_length)  # 包头
        if data_start == FRAMEFLAG.START_FLAG:  #
            data_header = self.recv_bytes(self.header_length)  # 包头长度
            if data_header is not None:
                data_end_length = convert_bytes_to_int(data_header[-4:]) + self.start_length + 1
                data_end = self.recv_bytes(data_end_length)  # 包内容
                if data_header is not None:
                    if data_end[-2:] == FRAMEFLAG.END_FLAG:  # 包结尾
                        try:
                            package = unpack_frame(data_start + data_header + data_end)
                            if 'handle_data' in self.config.CALL_BACK.keys():
                                self.config.CALL_BACK['handle_data'](self, package)
                        except:
                            pass

    @daemon_thread
    def receive(self):
        while self.exit_flag is False:
            try:
                if 'handle_read' in self.config.CALL_BACK.keys():
                    data = self.sock.recv(self.config.BUFFER)
                    if data is None or len(data) == 0:
                        self.handle_close(f"remote close")
                    elif data is not None and len(data) > 0:
                        self.config.CALL_BACK['handle_read'](self, data)
                else:
                    self.recv_default()
            except Exception as e:
                self.handle_error(e)
        self.handle_close(f"")
        
    def send(self, data: bytes):
        with self.lock:
            if self.sock:
                length = len(data)
                buffer = self.config.BUFFER
                group = int(length/buffer)
                for i in range(group):
                    self.sock.send(data[i*buffer: (i+1)*buffer])
                if group*buffer < length:
                    self.sock.send(data[group*buffer:])
                return length
            raise Exception(f"no connect")
    
    def check_invalid(self) -> bool:
        return self.valid


class SocketIPAccssor:

    def __init__(self, config: SocketConfig):
        self.config = config
        self.accessor = None
        self.exit_flag = False
        self.thread = None
        self.sockets = {}
        self.lock = Lock()

    def __del__(self):
        self.exit()

    def exit(self):
        self.exit_flag = True
        for socket in self.sockets.values():
            socket.close()
        if self.accessor:
            self.accessor.close()
        self.accessor = None
        self.thread = None
        self.sockets = {}

    def create_client(self):
        with self.lock:
            if self.config.MODE == SocketType.TCP_CLIENT:
                self.accessor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif self.config.MODE == SocketType.UDP_CLIENT:
                self.accessor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.accessor.settimeout(self.config.TIME_OUT)  # 设置连接超时
            self.accessor.connect((self.config.HOST, self.config.PORT))
            self.accessor.settimeout(None)

            self.sockets[f"{self.config.HOST}:{self.config.PORT}"] = SocketIPHandler(self.config, self.accessor)
        
    def create_server(self):
        with self.lock:
            if self.config.MODE == SocketType.TCP_SERVER:
                self.accessor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif self.config.MODE == SocketType.UDP_SERVER:
                self.accessor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.accessor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.accessor.bind((self.config.HOST, self.config.PORT))

            if self.config.MODE == SocketType.TCP_SERVER:
                self.accessor.listen(self.config.LISTEN)

        while self.exit_flag is False:
            try:
                sock, addr = self.accessor.accept()  # 接收连接
                if self.verify_request(sock, addr) is True:
                    self.sockets[f"{addr[0]}:{addr[1]}"] = SocketIPHandler(self.config, sock, addr)
            except:
                pass

    def verify_request(self, sock, address):
        return True

    def clear_invalid(self):
        sock_addrs = list(self.sockets.keys())
        for sock_addr in sock_addrs:
            if sock_addr in self.sockets.keys() and self.sockets[sock_addr].check_invalid() is False:
                del self.sockets[sock_addr]

    def start(self, thread: bool = True):
        if self.config.MODE in [SocketType.TCP_SERVER, SocketType.UDP_SERVER]:
            if thread is True:
                self.thread = Thread(target=self.create_server)
            else:
                self.create_server()
        else:
            if thread is True:
                self.thread = Thread(target=self.create_client)
            else:
                self.create_client()

        if thread is True and self.thread:
            self.thread.start()