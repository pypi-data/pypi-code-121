from minio import Minio
import os
import io

class PyMinio:
    def __init__(self, host, port, access_key, secret_key, secure=False):
        self.client = Minio(
            "{}:{}".format(host, port),
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def set_bucket(self, bucket):
        self.bucket = bucket

    def _trim_bucket(self, object_name:str, *, trim:bool) -> str:
        if object_name[0]=='/':
            object_name = object_name[1:]
            
        # 去掉前面的桶的名字
        if trim==True:
            arr = object_name.split('/')[1:]
            object_name = os.path.join(*arr)

        return object_name

    def download(self, object_name:str, local_name:str, *, trim:bool=False) -> bool:
        object_name = self._trim_bucket(object_name, trim=trim)

        if self.exists(object_name):
            self.client.fget_object(self.bucket, object_name, local_name)
            return True
        else:
            return False

    def upload(self, file_path:str, object_name:str) -> bool:
        if self.client.bucket_exists(self.bucket) == False:
            self.client.make_bucket(self.bucket)  # 生成一个bucket，类似文件夹

        self.client.fput_object(
            bucket_name=self.bucket,
            object_name=object_name,
            file_path=file_path
        )
        return True

    def write(self, object_name, content:bytes):
        self.client.put_object(self.bucket, object_name, io.BytesIO(content), len(content))

    def exists(self, object_name:str, *, trim:bool=False) -> bool:
        object_name = self._trim_bucket(object_name, trim=trim)

        try:
            response = self.client.get_object(self.bucket, object_name)
            response.close()
            response.release_conn()
            return True
        except Exception as e:
            return False

    # 删除对象
    def remove_file(self, object_name:str, *, trim:bool=False) -> bool:
        object_name = self._trim_bucket(object_name, trim=trim)
        try:
            self.client.remove_object(self.bucket, object_name)
            #print("Sussess")
            return True
        except Exception as err:
            #print(err)
            return False

    def get_client(self) -> Minio:
        return self.client
