from pydantic import BaseModel
from loguru import logger

class Logger(BaseModel):
    level: str = 'INFO'
    retention: str = '7 days'
    compression: str = 'zip'
    rotation: str = '00:00'
    log_path: str = "/var/log"

    def initial(self, filename):
        filename = '{}/{}'.format(self.log_path, filename)
        logger.add(filename, rotation=self.rotation, retention=self.retention, compression=self.compression, level=self.level)

        return logger

