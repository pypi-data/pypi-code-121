import typing
import copy
from .ZoneSenderObject import ZoneSenderObject

class SomeipPackage(ZoneSenderObject):
    ''' someip 发送或接收的数据
    '''
    def __init__(
        self, 
        service_name: 'str' = '',
        instance_id: 'int' = -1,
        interface_name: 'str' = '',
        interface_type: 'str' = '',
        context: 'dict' = {}) -> None:
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