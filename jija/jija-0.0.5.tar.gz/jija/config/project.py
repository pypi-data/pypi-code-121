from jija.config.base import Base


class ProjectConfig(Base):
    SECRET_KEY = None

    def __init__(self, *, secret_key=b'*' * 32, **kwargs):
        ProjectConfig.SECRET_KEY = secret_key
        super().__init__(**kwargs)
