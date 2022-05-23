from .ZoneSenderObject import ZoneSenderObject

class CanStackConfig(ZoneSenderObject):
    ''' CanStack 配置类
    '''
    def __init__(
        self, 
        channel: 'int',
        is_fd: 'bool',
        bitrate: 'int' = 500000,
        fd_bitrate: 'int' = 2000000,
        bus_type: 'str' = 'vector',
        app_name: 'str' = 'ZoneSender') -> None:
        super().__init__()
        self.channel = channel
        self.isFd = is_fd
        self.bitrate = bitrate
        self.fdBitrate = fd_bitrate
        self.busType = bus_type
        self.appName = app_name

