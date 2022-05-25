import socket
import sys
import logging
import time
from copy import deepcopy
logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s", level=logging.DEBUG)

IP_RECVERR = 11
IP_RECVTTL = 12
MSG_ERRQUEUE    = 0x2000
TTL_EXPIRED = 11
DESTINATION_UNREACHABLE = 3
ERROR_REASON_ICMP = 2
ICMP_TYPE_OFFSET=5
DEFAULT_MAX_TTL= 1
DEFAULT_TRACEROUTE_TIMEOUT= 0.2


class DestinationUnreachable(Exception):
    pass

class DebugSocket(socket.socket):
    global_settings={}
    default_settings={
            'enabled':False,
            'debug':False,
            'error_handling':False,
            'auto_traceroute': False,
            'static_source_port': False,
            'initial_ttl': 64
        }
    socket_list=[]
    


    def __init__(self, family=-1, type=-1, proto=-1, fileno=None):
        self._log=logging.getLogger(__file__)
        self._global_index=len(self.socket_list)
        self._log.debug(f'Created Socket with global index {self._global_index}')
        if self._global_index not in self.global_settings:
            super().__init__(family, type, proto, fileno)
            self.settings=deepcopy(self.default_settings)
            return None
        self.socket_list.append(self)
        for k,v in self.default_settings.items():
            if k not in self.global_settings[self._global_index]:
                self.global_settings[self._global_index][k]=v

        self.settings=self.global_settings[self._global_index]
        super().__init__(family, type, proto, fileno)
       
        self.__ttl=self.settings['initial_ttl']
        self._dst_address=None
        self._dst_port=None
        self._src_address=None
        self._src_port=None
        self._last_sent_bytes=None
        self._last_sent_flags=None
        self._last_error=None
        # self._socket_infos={
        #     'src_ip':None,
        #     'dst_ip':None,
        #     'src_port': None,
        #     'dst_port':None,
        #     'hops':[]
        # }
        self._hops=[]
        self._last_send_time=None
        self._last_roundtrip_time=None
        
        
        
    @property
    def src_port(self,port):
        self._src_port=port

    def bind_source_port(self):
        if self._src_port:
            if self._src_address:
                self.bind((self._src_address,int(self._src_port)))
                self._log.debug(f'Bound to static source port {self._src_address}:{self._src_port}')
                
            else:
                self.bind(('0.0.0.0',int(self._src_port)))
                self._log.debug(f'Bound to static source port 0.0.0.0:{self._src_port}')
        else:
            self._log.debug(f'No static source port defined using dynamic ephemeral port')
        
    def set_ttl(self,ttl):
        self._log.debug(f'Setting TTL to {ttl}')
        self.__ttl=ttl
        self.setsockopt(socket.SOL_IP, socket.IP_TTL, self.__ttl)
    
    def enable_error_handling(self):
        self.setsockopt(socket.IPPROTO_IP, IP_RECVERR, int(True))
        self.setsockopt (socket.SOL_IP, IP_RECVTTL, int(True))
        self._log.debug('Enabled IP_RECVERR and IP_RECVTTL flags on socket')

    def connect(self, __address):
        if not self.settings['enabled']:
            return super().connect(__address)
        
        self._dst_address=__address[0]
        self._dst_port=__address[1]
        if self.settings['static_source_port']:
            self._src_port=int(self.settings['static_source_port'])
        self.bind_source_port()
        con=super().connect(__address)
        self._src_address, self._src_port=self.getsockname()
        self._log.debug(f'Opened connection from {self._src_address}:{self._src_port} to {self._dst_address}:{self._dst_port}')
        return con    

    def send(self,bytes,flags=0):
        if not self.settings['enabled']:
            return super().send(bytes,flags)

        self.set_ttl(self.__ttl)
        self._log.debug(f'Sending {len(bytes)} bytes from {self._src_address}:{self._src_port} to {self._dst_address}:{self._dst_port}')
        if self.settings['debug'] == 'packet':
            hex_data=':'.join(format(c, '02x') for c in bytes)
            self._log.debug(f'Packet data: {hex_data}')
        self._last_sent_bytes=bytes
        self._last_sent_flags=flags
        self._last_error=None
        if self.settings['error_handling']:
            self.enable_error_handling()
        self._last_send_time=round(time.time() * 1000,2)
        result=super().send(bytes,flags)

        return result
    
    def get_network_hops(self):
        return self._socket_infos['hops']
    
    def handle_ancdata(self, ancdata):
        try: 
            if ancdata[0][1] == ERROR_REASON_ICMP:
                if len(ancdata) == 1:
                    reporting_ip = self._dst_address
                elif ancdata[1][2][ICMP_TYPE_OFFSET] == TTL_EXPIRED:
                    reporting_ip='.'.join([str(i) for i in ancdata[1][2][20:24]])
                    self._log.error (f'Got ICMP error TTL_EXPIRED from {reporting_ip} RTT {self._last_roundtrip_time} ms')
                    self._last_error='TTL_EXPIRED'
                    if self.__ttl == 1:
                        self._hops=[]
                elif ancdata[1][2][ICMP_TYPE_OFFSET] == DESTINATION_UNREACHABLE:
                    reporting_ip='.'.join([str(i) for i in ancdata[1][2][20:24]])
                    self._last_error='DESTINATION_UNREACHABLE'
                    self._log.error (f'got ICMP error DESTINATION_UNREACHABLE from {reporting_ip} RTT {self._last_roundtrip_time} ms')
                
        except Exception:
            self._log.error (f'Cannot parse ancdata {ancdata}')
        self._hops.append(
            [self.__ttl,reporting_ip,self._last_roundtrip_time]
        )            
        return reporting_ip


    def recv(self,max_packet_size):
        if not self.settings['enabled']:
            return super().recv(max_packet_size)
        self._last_roundtrip_time=round(time.time() * 1000 - self._last_send_time,4)
        try:
            data, ancdata, msg_flags, address = super().recvmsg(max_packet_size, 65535)
            self.handle_ancdata(ancdata)
        except OSError as e:
            data, ancdata, msg_flags, address = self.recvmsg(max_packet_size, 65535, MSG_ERRQUEUE)
            reporting_ip=self.handle_ancdata(ancdata)
            if self._last_error == 'TTL_EXPIRED':
                if self.settings['auto_traceroute']:
                    self.__ttl+=1
                    self._log.debug(f'Auto traceroute enabled. Resending packet with TTL {self.__ttl}')
                    
                    self.send(self._last_sent_bytes, self._last_sent_flags)
                    return self.recv(max_packet_size)
            elif self._last_error == 'DESTINATION_UNREACHABLE':
                raise DestinationUnreachable
        return data
    
    # def __del__(self):
    #     if not self.settings['enabled']:
    #     self._log.debug('Delete socket index {self._global_index}')
    #     self.socket_list.pop(self._global_index)
    #     del self.global_settings[self._global_index]
    #     return super().__del__()

# register socketPlus
sys.modules['socket'].socket=DebugSocket
# print(dir(sys.modules['socket']))
