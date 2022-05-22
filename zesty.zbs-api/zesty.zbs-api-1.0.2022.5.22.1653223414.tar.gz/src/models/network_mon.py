

class NetworkMonitor:
    bytes_sent = None
    bytes_recv = None
    packets_sent = None
    packets_recv = None

    def __init__(self, net_mon_data):
        self.bytes_sent = net_mon_data.get('bytes_sent')
        self.bytes_recv = net_mon_data.get('bytes_recv')
        self.packets_sent = net_mon_data.get('packets_sent')
        self.packets_recv = net_mon_data.get('packets_recv')

    def to_dict(self):
        return self.__dict__
