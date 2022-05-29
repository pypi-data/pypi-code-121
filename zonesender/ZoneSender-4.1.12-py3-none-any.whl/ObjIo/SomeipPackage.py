import typing
import copy
from .ZoneSenderObject import ZoneSenderObject

class SomeipPackage(ZoneSenderObject):
    ''' someip 发送或接收的数据

    :param service_name: str Someip服务名
    :param instance_id: int Someip Instance ID
    :param interface_name: str Someip 接口名
    :param interface_type: str 接口类型'method'|'get'|'set'|'notifer'|'event'
    :param context: dict 序列化后的数据 Dict
    :param payload: bytes 未序列化的原始 Bytes
    '''
    def __init__(
        self, 
        service_name: 'str' = '',
        instance_id: 'int' = -1,
        interface_name: 'str' = '',
        interface_type: 'str' = '',
        context: 'dict' = {},
        *args, **kwargs) -> None:
        #########################
        super().__init__()
        self.serviceName = service_name
        self.srcIp = ''
        self.srcPort = -1
        self.destIp = ''
        self.destPort = -1
        self.interfaceType = interface_type
        self.serviceId = -1
        self.instanceId = instance_id
        self.interfaceId = -1
        self.interfaceName = interface_name
        self.context = context
        self.payload = kwargs.get('payload', bytes())
    
    def __str__(self) -> str:
        # return super().__str__()
        # return '{0} {1} {2}'.format(self.serviceName, self.interfaceName, self.context)
        return \
        '''
srcIp: {0}
srcPort: {1}
destIp: {2}
destPort: {3}
type: {4}
serviceId: {5}
serviceName: {6}
instanceId: {7}
interfaceId: {8}
interfaceName: {9}
context: {10}
        '''.format(
            self.srcIp,
            self.srcPort,
            self.destIp,
            self.destPort,
            self.interfaceType,
            self.serviceId,
            self.serviceName,
            self.instanceId,
            self.interfaceId,
            self.interfaceName,
            self.context
        )

    @staticmethod
    def From(obj) -> 'SomeipPackage':
        ''' 从其他对象中构建 SomeipPackage
        :param obj: dict 表达 Someip 的 dict 对象
        '''
        if (isinstance(obj, dict)):
            someip_package_ = SomeipPackage(obj['sv_name'])
            someip_package_.srcIp = obj['src_ip']
            someip_package_.srcPort = obj['src_port']
            someip_package_.destIp = obj['dest_ip']
            someip_package_.destPort = obj['dest_port']
            someip_package_.interfaceType = obj['if_type']
            someip_package_.serviceId = obj['sv_id']
            someip_package_.instanceId = obj['ince_id']
            someip_package_.interfaceId = obj['if_id']
            someip_package_.interfaceName = obj['if_name']
            someip_package_.context = obj['context']
            someip_package_.payload = obj.get('payload', bytes())
            return someip_package_
        raise TypeError

    def ToDict(self) -> 'dict':
        return {
            'sv_name': self.serviceName,
            'src_ip': self.srcIp,
            'src_port': self.srcPort,
            'dest_ip': self.destIp,
            'dest_port': self.destPort,
            'if_type': self.interfaceType,
            'sv_id': self.serviceId,
            'ince_id': self.instanceId,
            'if_id': self.interfaceId,
            'if_name': self.interfaceName,
            'context': self.context,
            'payload': self.payload,
        }

    @staticmethod
    def CopyData(someip_src: 'SomeipPackage', someip_dist: 'SomeipPackage') -> None:
        ''' 将 someip_src 的数据复制到 someip_dist 中
        '''
        someip_dist.serviceName = someip_src.serviceName
        someip_dist.srcIp = someip_src.srcIp
        someip_dist.srcPort = someip_src.srcPort
        someip_dist.destIp = someip_src.destIp
        someip_dist.destPort = someip_src.destPort
        someip_dist.interfaceType = someip_src.interfaceType
        someip_dist.serviceId = someip_src.serviceId
        someip_dist.instanceId = someip_src.instanceId
        someip_dist.interfaceId = someip_src.interfaceId
        someip_dist.interfaceName = someip_src.interfaceName
        someip_dist.context = someip_src.context
        someip_dist.payload = someip_src.payload