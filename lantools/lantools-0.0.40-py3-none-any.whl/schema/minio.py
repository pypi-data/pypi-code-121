from pydantic import BaseModel
from .. import minio 

class Minio(BaseModel):
    host: str
    port: int
    bucket: str
    access_key: str
    secret_key: str

    def connect(self):
        # 初始化minio对象
        obj = minio.PyMinio(
            self.host,
            self.port,
            self.access_key,
            self.secret_key,
        )
        obj.set_bucket(self.bucket)
        return obj