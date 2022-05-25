
class MQTTConfig:

    def __init__(self,
                 client_id: str,
                 address: str = "localhost",
                 port: int = 1883,
                 keep_alive: int = 60,
                 prefix: str = '/'):
        self.address = address
        self.port = port
        self.keep_alive = keep_alive
        self.prefix = prefix.rstrip('/')
        self.client_id = client_id
