import typer
import oss2
from typing import Optional
from enum import Enum
import zipfile
import os
from rich.console import Console
from rich.table import Column, Table


def zip_all_files(dir,zipFile,pre_dir):
    """递归压缩文件夹下的所有文件
    参数:
    - dir: 要压缩的文件夹路径
    - zipFile: zipfile对象
    - pre_dir: 压缩文件根目录
    """
    for f in os.listdir(dir):
        absFile=os.path.join(dir,f) #子文件的绝对路径
        pre_d = os.path.join(pre_dir,f)
        if os.path.isdir(absFile): #判断是文件夹，继续深度读取。
            zipFile.write(absFile, pre_d) #在zip文件中创建文件夹
            zip_all_files(absFile,zipFile, pre_dir=pre_d) #递归操作
        else: #判断是普通文件，直接写到zip文件中。
            zipFile.write(absFile, pre_d)

default_access_key_id = 'LTAI5tPsMSE5G3srWxB8j3yw'
default_access_key_secret = 'z5jPdkfNq4WPtV4c7YaAJwH5Sj45gT'
default_endpoint = 'http://oss-cn-beijing.aliyuncs.com'
default_data_bucket = 'deepset'
default_model_bucket = 'pretrained-model'
default_asset_bucket = 'deepasset'

class OSSStorer:
    '''阿里云oss对象存储'''
    def __init__(
        self, 
        access_key_id : str = default_access_key_id,
        access_key_secret : str = default_access_key_secret, 
        endpoint :str = default_endpoint, 
        data_bucket : str = default_data_bucket,
        model_bucket : str = default_model_bucket,
        asset_bucket : str = default_asset_bucket
        ):
        super().__init__()
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.data_bucket = oss2.Bucket(self.auth, endpoint, data_bucket)
        self.model_bucket = oss2.Bucket(self.auth, endpoint, model_bucket)
        self.assets_bucket = oss2.Bucket(self.auth, endpoint, asset_bucket)


    def list_all_assets(self):
        """获取数据名称"""
        all_asset = []
        for obj in oss2.ObjectIterator(self.assets_bucket):
            asset = obj.key.split('.')[0]
            all_asset.append(asset)
        return all_asset


    def list_all_datasets(self):
        """获取所有数据集名称"""
        all_data = []
        for obj in oss2.ObjectIterator(self.data_bucket):
            data = obj.key.split('.')[0]
            all_data.append(data)
        return all_data
    
    def list_all_plms(self):
        """获取所有预模型名称"""
        all_model = []
        for obj in oss2.ObjectIterator(self.model_bucket):
            model = obj.key.split('.')[0]
            all_model.append(model)
        return all_model


    def download_dataset(
        self, 
        dataset:str, 
        localpath: str='./datasets/'):
        """下载数据集
        - dataset: 数据集名称
        - localpath: 下载到本地的路径 默认为./datasets/
        """
        if not os.path.exists(localpath):
            os.makedirs(localpath)
        file = dataset + '.zip'
        file_path = localpath + file
        dataset_path = localpath + dataset
        if not os.path.exists(dataset_path):
            try:
                self.data_bucket.get_object_to_file(key=file, filename=file_path)
                with zipfile.ZipFile(file=file_path, mode='r') as zf:
                    zf.extractall(path=localpath)
            finally:
                if os.path.exists(file_path):
                    os.remove(path=file_path)


    def download_plm(
        self, 
        model:str, 
        localpath: str = './plms/'):
        """下载预训练模型
        - model: 模型名称
        - localpath: 下载到本地的路径 默认为./plms/
        """
        if not os.path.exists(localpath):
            os.makedirs(localpath)
        file = model + '.zip'
        file_path = localpath + file
        model_path = localpath + model
        if not os.path.exists(model_path):
            try:
                self.model_bucket.get_object_to_file(key=file, filename=file_path)
                with zipfile.ZipFile(file=file_path, mode='r') as zf:
                    zf.extractall(path=localpath)
            finally:
                if os.path.exists(file_path):
                    os.remove(path=file_path)
                


    def download_asset(
        self, 
        asset:str, 
        localpath: str = './assets/'):
        """下载assets
        - asset: 资产名称
        - localpath: 下载到本地的路径 默认为./assets/
        """
        if not os.path.exists(localpath):
            os.makedirs(localpath)
        file = asset + '.zip'
        file_path = localpath + file
        asset_path = localpath + asset
        if not os.path.exists(asset_path):
            try:
                self.assets_bucket.get_object_to_file(key=file, filename=file_path)
                with zipfile.ZipFile(file=file_path, mode='r') as zf:
                    zf.extractall(path=localpath)
            finally:
                if os.path.exists(file_path):
                    os.remove(path=file_path)
                
        

    def upload_dataset(
        self, 
        dataset:str, 
        localpath: str = 'datasets/'):
        """上传数据集
        - dataset: 数据集名称
        - localpath: 数据集路径, 默认为datasets/
        """
        file = dataset + '.zip'
        file_path = localpath + file
        dataset_path = localpath + dataset
        with zipfile.ZipFile(file=file_path, mode='w') as z:
            zip_all_files(dataset_path, z, pre_dir=dataset)
        self.data_bucket.put_object_from_file(key=file, filename=file_path)
        if os.path.exists(file_path):
            os.remove(path=file_path)


    def upload_pretrained(
        self, 
        model, 
        localpath: str = 'plms/'):
        """上传预训练模型
        - model: 模型名称
        - localpath: 预训练模型路径, 默认为plms/
        """
        file = model + '.zip'
        file_path = localpath + file
        model_path = localpath + model
        # 注意如果不用with 语法, 如果没有关闭zip文件则解压会报错
        with zipfile.ZipFile(file=file_path, mode='w') as z:
            zip_all_files(model_path, z, model)
        self.model_bucket.put_object_from_file(key=file, filename=file_path)
        if os.path.exists(file_path):
            os.remove(path=file_path)


    def upload_asset(
        self,
        asset,
        localpath: str = './assets/'
    ):
        """上传原始数据
        - asset: 数据名称
        - localpath: 数据的路径, 默认为./assets/
        """
        file = asset + '.zip'
        file_path = localpath + file
        asset_path = localpath + asset
        with zipfile.ZipFile(file=file_path, mode='w') as z:
            zip_all_files(asset_path, z, asset)
        self.assets_bucket.put_object_from_file(key=file, filename=file_path)
        if os.path.exists(file_path):
            os.remove(path=file_path)


    
class DataType(str, Enum):
    dataset = 'dataset'
    asset = 'asset'
    plm = 'plm'


oss = OSSStorer()
app = typer.Typer(help="OSS storage")


@app.command('download')
def download(name: str, type: DataType= DataType.dataset, path: Optional[str]= None) -> None:
    """下载数据
    """
    if type == 'dataset':
        if not path:
            path = './datasets/'
        oss.download_dataset(dataset=name, localpath=path)
        
    elif type == 'asset':
        if not path:
            path = './assets/'
        oss.download_asset(asset=name, localpath=path)
    elif type == 'plm':
        if not path:
            path = './plms/'
        oss.download_plm(plm=name, localpath=path)
    
    
@app.command('list')
def list(type : DataType) -> None:
    """显示数据
    """
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column(f"{type}", style="dim", width=25)
        
    if type == "dataset":
        datasets = oss.list_all_datasets()
        for ds in datasets:
            table.add_row(ds)
        console.print(table)
        # typer.echo(datasets)
    elif type == "asset":
        assets = oss.list_all_assets() 
        for asset in assets:
            table.add_row(asset) 
        console.print(table)
    elif type == "plm":
        plms = oss.list_all_plms()
        for plm in plms:
            table.add_row(plm)
        console.print(table)

@app.command('upload')
def upload(name: str, type: DataType = DataType.dataset,  path: str = None ) -> None:
    """上传数据
    """
    if type == 'dataset':
        if path is None:
            path = './datasets/'
        oss.upload_dataset(dataset=name, localpath=path)
    elif type == 'asset':
        if path is None:
            path = './assets/'
        oss.upload_asset(asset=name, localpath=path)
    elif type == 'plm':
        if path is None:
            path = './plms/'
        oss.upload_pretrained(model=name, localpath=path)
    
if __name__ == "__main__":
    app()
    

    
    




