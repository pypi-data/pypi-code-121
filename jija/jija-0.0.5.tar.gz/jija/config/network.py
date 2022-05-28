from jija.config.base import Base


class NetworkConfig(Base):
    HOST = None
    PORT = None

    def __init__(self, *, host='0.0.0.0', port=8080, **kwargs):
        NetworkConfig.HOST = host
        NetworkConfig.PORT = port

        super().__init__(**kwargs)
