#coding=utf-8
from hdfs.client import Client
#from hdfs import Config


class HdfsService:
    def __init__(self,url,root):
        self.url=url
        self.client=None
        self.root=root if root is not None else '/'


    def __connect__(self,path=None):
        if self.client is None:
            #config=hdfs.config.Config()
            #self.client=config.get_client()
            self.client=Client(self.url,root=self.root,timeout=60000)
            #self.client = KerberosClient(self.url, root="/")



    # 读取hdfs文件内容,将每行存入数组返回
    def cat(self, filename):
        # with client.read('samples.csv', encoding='utf-8', delimiter='\n') as reader:
        #  for line in reader:
        # pass
        self.__connect__()
        lines = []
        with self.client.read(filename, encoding='utf-8', delimiter='\n') as reader:
            for line in reader:
                # pass
                # print line.strip()
                lines.append(line.strip())
        return lines

    # 创建目录
    def mkdir(self, hdfs_path):
        self.__connect__()
        self.client.makedirs(hdfs_path)

    # 删除hdfs文件
    def rm(self, hdfs_path):
        self.__connect__()
        self.client.delete(hdfs_path)

    # 上传文件到hdfs
    def put(self,local_path, hdfs_path):
        self.__connect__()
        self.client.upload(hdfs_path, local_path)

    # 从hdfs获取文件到本地
    def get(self, hdfs_path, local_path):
        self.__connect__()
        self.client.download(hdfs_path, local_path, overwrite=False)

    # 追加数据到hdfs文件
    def append(self, hdfs_path, data):
        self.__connect__()
        self.client.write(hdfs_path, data, overwrite=False, append=True, encoding='utf-8')

    # 覆盖数据写到hdfs文件
    def write(self, hdfs_path, data):
        self.__connect__()
        self.client.write(hdfs_path, data, overwrite=True, append=False, encoding='utf-8')

    # 移动或者修改文件
    def mv(self, hdfs_src_path, hdfs_dst_path):
        self.__connect__()
        self.client.rename(hdfs_src_path, hdfs_dst_path)

    # 返回目录下的文件
    def ls(self, hdfs_path):

        self.__connect__()
        return self.client.list(hdfs_path, status=False)

if __name__ == '__main__':
    svc=HdfsService('http://wyx.inhandcloud.com:9870',root="/")
    result=svc.ls("/")
    print(result)
    svc.mkdir("/tube_data2")
    result=svc.ls("/tube_data")
    print(result)
    #hdfs.put('/Users/han/temp/jquery-validation-1.19.1.zip','/tube_data')
    svc.put('/home/han/temp/gehc_ib.1595030785.csv','/tmp')
    result=svc.ls("/tube_data")
    print(result)
