import os.path
from typing import Union
from os import getpid, makedirs
from typing import Union

from fastapi import FastAPI
from fastapi import APIRouter
from httpx import Client as httpClient
from httpx import AsyncClient as asyncHttpClient

from mfhm.log import getLogger
from mfhm.metadata import TransmissionType, TransmissionTypeField
from mfhm.errors import PathError,OnlineError


class BasicServices(FastAPI):
    '''
    服务基类
    '''

    def __init__(
            self,
            serviceName:str,
            serviceHost:str = '0.0.0.0',
            servicePort:int = 21429,
            dataDir:str = None,
            httpClient:httpClient = None,
            asyncHttpClient:asyncHttpClient = None,
            *args,
            **kwargs
    ) -> None:
        self.serviceName = serviceName
        self.serviceHost = serviceHost
        self.servicePort = servicePort
        self.servicePid = None
        self.dataDir = dataDir
        self.httpClient = httpClient
        self.asyncHttpClient = asyncHttpClient
        self.transmissionType = None
        self.transmissionData = None
        super().__init__(*args, **kwargs)

    @property
    def dataDir(self):
        return self.__dataDir

    @dataDir.setter
    def dataDir(self, value: Union[str, None]):
        # 未指定数据存储目录时, 无需做任何处理
        if value == None:
            self.__dataDir = None
            return None

        if not isinstance(value, str):
            raise ValueError(f'Args "dataDir" should be a value of type {str}')

        # 如果提供了一个已存在的路径
        if os.path.exists(value):
            # 且路径指向一个文件
            if os.path.isfile(value):
                raise PathError(f'The "{value}" path points to a file, this path cannot be used as a data storage directory')
        # 否则创建目录
        else:
            self.__makeSureDir(value)

        self.__dataDir = value

    @staticmethod
    def __makeSureDir(dirPath:str) -> None:
        '''
        确保目录存在, 如果dirPath已存在则忽略, 否则将会创建目录
        '''
        try:
            makedirs(dirPath)
        except Exception as err:
            pass

    def start(self):
        '''
        启动服务
        '''
        import uvicorn

        self.servicePid = getpid()

        # 覆盖uvicorn默认日志配置, 转用log模块提供的日志处理程序, 
        # 统一日志格式
        logConfig = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    '()': 'mfhm.log.Formatter'
                }
            },
            'handlers': {
                'default': {
                    'formatter': 'default',
                    'class': 'mfhm.log.ConsoleHighlightedHandler',
                }
            },
            'loggers': {
                'uvicorn': {
                    'handlers': ['default'],
                    'level': 'INFO'
                },
                'uvicorn.error': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': False
                },
                'uvicorn.access': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }

        uvicorn.run(
            self,
            host=self.serviceHost,
            port=self.servicePort,
            log_config=logConfig
        )


class Service(BasicServices):
    '''
    微服务类, 一个类实例代表一个微服务
    '''

    def __init__(
            self, 
            serviceName: str, 
            serviceHost: str = '0.0.0.0', 
            servicePort: int = 21429, 
            centerConfig: dict = None,
            dataDir:str = None,
            httpClient: httpClient = httpClient(), 
            logger = getLogger(os.path.basename(os.path.abspath(__file__)))
    ) -> None:
        '''
        Args:
            serviceName: 服务名称
            serviceHost: 服务主机地址(监听地址)
            servicePort: 服务端口(监听端口)
            centerUri: 服务中心连接字符串
            dataDir: 数据存储目录
            httpClient: HTTPX同步客户端
        '''
        self.centerConfig = centerConfig
        self.logger = logger

        # 不指定服务中心配置时使用默认配置
        if self.centerConfig == None:
            self.centerConfig = {
                'host': '127.0.0.1',
                'port': 21428,
                'transmissionType': None,
                'transmissionData': None
            }

        super().__init__(
            serviceName=serviceName, 
            serviceHost=serviceHost, 
            servicePort=servicePort, 
            dataDir=dataDir,
            httpClient=httpClient
        )

        # 服务退出时发送下线请求
        self.add_event_handler('shutdown', self.offline)

    def online(self) -> None:
        '''
        向服务中心发出上线请求
        '''
        headers = {}

        # 如果服务中心启用了传输认证
        if self.centerConfig['transmissionType']:
            # 且传输认证类型是密钥验证
            if self.centerConfig['transmissionType'] == TransmissionType.authKey:
                # 请求头中携带服务中心的传输验证密钥
                headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = self.centerConfig['transmissionData']

        # 当前服务的所有路由
        methods = {}
        for route in self.routes:
            methods[route.name] = {'path': route.path, 'methods': list(route.methods)}

        url = f'http://{self.centerConfig["host"]}:{self.centerConfig["port"]}/online'
        try:
            response = self.httpClient.post(url, headers=headers, json={
                'name': self.serviceName,
                'port': self.servicePort,
                'transmissionType': self.transmissionType,
                'transmissionData': self.transmissionData,
                'methods': methods
            }, timeout=5)
        except Exception as err:
            errorMessage = f'Service online failure, unable to communicate properly with the service center: {err}'
            self.logger.critical(errorMessage)
            raise OnlineError(errorMessage)

        if not response.status_code == 200:
            errorMessage = f'The service has failed to go live, and the service center has returned an error:\n'
            errorMessage += f'    HTTP code: {response.status_code}\n'
            errorMessage += f'    Data: {response.text}\n'
            self.logger.critical(errorMessage)
            raise OnlineError(errorMessage)

        responseData = response.json()
        if not responseData['code'] == 0:
            errorMessage = f'The service has failed to go live, and the service center has returned an error:\n'
            errorMessage += f'    Status code: {responseData["code"]}\n'
            errorMessage += f'    Message: {responseData["message"]}\n'
            self.logger.critical(errorMessage)
            raise OnlineError(errorMessage)

    def offline(self) -> None:
        '''
        服务下线
        '''
        headers = {}

        # 如果服务中心启用了传输认证
        if self.centerConfig['transmissionType']:
            # 且传输认证类型是密钥验证
            if self.centerConfig['transmissionType'] == TransmissionType.authKey:
                # 请求头中携带服务中心的传输验证密钥
                headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = self.centerConfig['transmissionData']
        
        url = f'http://{self.centerConfig["host"]}:{self.centerConfig["port"]}/offline/{self.serviceName}/{self.servicePort}'
        try:
            self.httpClient.delete(url, headers=headers, timeout=5)
        except Exception as err:
            self.logger.warning(f'Service offline failed: {err}')

    async def ping(self):
        '''
        服务内置路由, 用于响应服务中心的ping测试
        '''
        return {'code': 0, 'message': 'ok'}

    def initApi(self):
        '''
        初始化API
        '''
        # 注册内置路由
        self.add_api_route('/ping', self.ping, methods=['GET'], name='ping')

    def start(self):
        self.online()
        super().start()


class SubService(APIRouter):
    '''
    子服务, 用于模块化/和自定义服务用途, 其本质上是
    FastAPI的APIRouter
    '''

    def __init__(
            self, 
            dataDir:str = None,
            httpClient:httpClient = None,
            asyncHttpClient:asyncHttpClient = None,
            *args,
            **kwargs
    ):
        '''
        Args:
            dataDir: 数据存储目录
            httpClient: HTTPX同步客户端
            asyncHttpClient: HTTPX异步客户端
        '''
        self.dataDir = dataDir
        self.httpClient = httpClient
        self.asyncHttpClient = asyncHttpClient
        super().__init__(*args, **kwargs)

    @property
    def dataDir(self):
        return self.__dataDir

    @dataDir.setter
    def dataDir(self, value: Union[str, None]):
        # 未指定数据存储目录时, 无需做任何处理
        if value == None:
            self.__dataDir = None
            return None

        if not isinstance(value, str):
            raise ValueError(f'Args "dataDir" should be a value of type {str}')

        # 如果提供了一个已存在的路径
        if os.path.exists(value):
            # 且路径指向一个文件
            if os.path.isfile(value):
                raise PathError(f'The "{value}" path points to a file, this path cannot be used as a data storage directory')
        # 否则创建目录
        else:
            self.__makeSureDir(value)

        self.__dataDir = value

    @staticmethod
    def __makeSureDir(dirPath:str) -> None:
        '''
        确保目录存在, 如果dirPath已存在则忽略, 否则将会创建目录
        '''
        try:
            makedirs(dirPath)
        except Exception as err:
            pass



