

class Status:

    ONLINE = 'online'
    OFFLINE = 'offline'

    def __init__(self, id: str, ip: str, status: str, _type: str = ''):
        self._type = 'status'
        self.id = id
        self.ip = ip
        self.status = status

        assert self.status in [self.ONLINE, self.OFFLINE]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Status):
            return other.id == self.id and other.ip == self.ip and other.status == self.status
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Status<id={self.id}, ip={self.ip}, status={self.status}>"
