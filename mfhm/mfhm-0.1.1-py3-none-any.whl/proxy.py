from typing import Tuple

from httpx import Client as httpClient
from httpx import AsyncClient as asyncHttpClient
from httpx import Request, Response

from mfhm.errors import ServiceCallError
from mfhm.metadata import TransmissionType, TransmissionTypeField


class OneCallProxy(object):
    '''
    单个服务调用代理, 一个实例表示一个服务调用
    '''

    def __init__(
            self, 
            serviceName: str,
            centerConfig: dict,
            httpClient: httpClient = httpClient(timeout=5),
            asyncHttpClient: httpClient = asyncHttpClient(timeout=5)
    ) -> None:
        '''
        Args:
            serviceName: 服务名称
            centerConfig: 服务中心配置
            httpClient: HTTPX的同步HTTP客户端
            asyncHttpClient: HTTPX的异步HTTP客户端
        '''
        self.serviceName = serviceName
        self.centerConfig = centerConfig
        self.httpClient = httpClient
        self.asyncHttpClient = asyncHttpClient
        self.name = None
        self.host = None
        self.port = None
        self.transmissionType = None
        self.transmissionData = None
        self.apiData = None

        # 实例化后载入服务数据
        self.reload()

    @staticmethod
    def __havePathParameter(url:str) -> bool:
        '''
        判断URL中是否存在路径参数

        Args:
            url: 待判断URL
        '''
        start = False
        for u in url:
            if u == '{':
                start = True
            if u == '}' and start:
                return True

        return False

    def __initCall(self, apiName: str, method: str, *args, **kwargs) -> Request:
        '''
        调用远程服务接口前的一些初始化工作, 返回一个 httpx.Request 对象

        Args:
            apiName: 服务的API名称
            method: API的HTTP调用方法
            *args, **kwargs: 接口参数
        '''
        # 判断待调用接口是否存在, 存在则从缓存中获取API信息
        apiName = apiName.strip()
        if not apiName in self.apiData:
            errorMessage = f'Service {self.serviceName} does not exist api {apiName}'
            raise ServiceCallError(errorMessage)
        apiInfo = self.apiData[apiName]
        
        # 如果API路径存在动态参数
        if apiInfo['haveParameter']:
            # 需要在请求参数中指定 pathparams 参数
            if not 'pathparams' in kwargs:
                errorMessage = f'API "{apiName}" is a dynamic path, you need to specify the value through the "pathparams" parameter'
                raise ServiceCallError(errorMessage) 
            # 替换路径参数, 得到真实调用路径
            apiInfo['path'] = apiInfo['path'].format(**kwargs['pathparams'])
            del kwargs['pathparams']

        headers = {}
        
        # 如果目标服务开启了传输包装
        if self.transmissionType:
            # 如果包装类型是密钥验证
            if self.transmissionType == TransmissionType.authKey:
                # 请求头插入验证密钥字段
                # 如果用户有传入自定义HTTP头, 则在自定义头HTTP的基础上插入密钥验证字段
                if 'headers' in kwargs:
                    headers = kwargs['headers']
                    del kwargs['headers']
                headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = self.transmissionData

        # 确定HTTP方法, 目标服务如果不支持, 抛出错误
        if not method.upper() in apiInfo['methods']:
            errorMessage = f'API "{apiName}" has no method "{method}"'
            raise ServiceCallError()
        
        # 构造请求对象并返回
        return Request(
            method=method.upper(),
            url=f'http://{self.host}:{self.port}{apiInfo["path"]}',
            headers=headers,
            *args, 
            **kwargs
        )

    def call(self, apiName: str, method: str, *args, **kwargs) -> Response:
        '''
        调用远程服务并返回一个 httpx.Response 对象

        Args:
            serviceName: 服务名称
            apiName: 服务的API名称
            method: API的HTTP调用方法
            *args, **kwargs: 接口参数
        '''
        requestObject = self.__initCall(apiName, method, *args, **kwargs)
        return self.httpClient.send(requestObject)

    async def asyncCall(self, apiName: str, method: str, *args, **kwargs) -> Response:
        '''
        异步调用远程服务并返回一个 httpx.Response 对象

        Args:
            serviceName: 服务名称
            apiName: 服务的API名称
            method: API的HTTP调用方法
            *args, **kwargs: 接口参数
        '''
        requestObject = self.__initCall(apiName, method, *args, **kwargs)
        return await self.asyncHttpClient.send(requestObject)

    def reload(self) -> None:
        '''
        重载服务调用信息
        '''
        headers = {}

        # 如果服务中心启用了包装
        if self.centerConfig['transmissionType']:
            # 如果服务中心的包装类型是密钥验证
            if self.centerConfig['transmissionType'] == TransmissionType.authKey:
                # 请求头中插入密钥验证字段
                 headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = self.centerConfig['transmissionData']

        if self.transmissionType == TransmissionType.authKey:
            # 且传输认证类型是密钥验证
            if self.centerConfig['transmissionType'] == TransmissionType.authKey:
                # 请求头中携带服务中心的传输验证密钥
                headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = self.transmissionData

        url = f'http://{self.centerConfig["host"]}:{self.centerConfig["port"]}/service/{self.serviceName}'
        try:
            serviceData = self.httpClient.get(url, headers=headers).json()
        except Exception as err:
            errorMessage = f'Unable to query service information: {err}'
            raise ServiceCallError(errorMessage)

        if serviceData['code'] == -1:
            errorMessage = f'Service "{self.serviceName}" not online'
            raise ServiceCallError(errorMessage)

        if not serviceData['code'] == 0:
            errorMessage = 'The service center returns an error status code\n'
            errorMessage += f'   Code: {serviceData["code"]}'
            errorMessage += f'   Message: {serviceData["message"]}'
            raise ServiceCallError(errorMessage)

        self.name = serviceData['name']
        self.host = serviceData['host']
        self.port = serviceData['port']
        self.transmissionType = serviceData['transmissionType']
        self.transmissionData = serviceData['transmissionData']

        # 新增haveParameter字段用于表示API是否存在路径参数
        for apiName in serviceData['methods']:
            if self.__havePathParameter(serviceData['methods'][apiName]['path']):
                serviceData['methods'][apiName]['haveParameter'] = True
            else:
                serviceData['methods'][apiName]['haveParameter'] = False

        self.apiData = serviceData['methods']

    async def asyncReload(self):
        '''
        重载服务调用信息(异步)
        '''
        headers = {}

        # 如果服务中心启用了包装
        if self.centerConfig['transmissionType']:
            # 如果服务中心的包装类型是密钥验证
            if self.centerConfig['transmissionType'] == TransmissionType.authKey:
                # 请求头中插入密钥验证字段
                 headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = self.centerConfig['transmissionData']

        url = f'http://{self.centerConfig["host"]}:{self.centerConfig["port"]}/service/{self.serviceName}'
        try:
            serviceData = await self.httpClient.get(url, headers=headers).json()
        except Exception as err:
            errorMessage = f'Unable to query service information: {err}'
            raise ServiceCallError(errorMessage)

        if serviceData['code'] == -1:
            errorMessage = f'Service "{self.serviceName}" not online'
            raise ServiceCallError(errorMessage)

        if not serviceData['code'] == 0:
            errorMessage = 'The service center returns an error status code\n'
            errorMessage += f'   Code: {serviceData["code"]}'
            errorMessage += f'   Message: {serviceData["message"]}'
            raise ServiceCallError(errorMessage)

        # 新增haveParameter字段用于表示API是否存在路径参数
        for apiName in serviceData['methods']:
            if self.__havePathParameter(serviceData['methods'][apiName]['path']):
                serviceData['methods'][apiName]['haveParameter'] = True
            else:
                serviceData['methods'][apiName]['haveParameter'] = False
        
        self.apiData = serviceData['methods']


class CallProxy(object):
    '''
    服务调用代理
    '''

    def __init__(
            self, 
            centerConfig: dict = None, 
            httpClient: httpClient = httpClient(timeout=5),
            asyncHttpClient: httpClient = asyncHttpClient(timeout=5)
    ) -> None:
        '''
        Args:
            centerConfig: 服务中心配置
            httpClient: HTTPX的同步HTTP客户端
            asyncHttpClient: HTTPX的异步HTTP客户端
        '''
        self.centerConfig = centerConfig
        self.httpClient = httpClient
        self.asyncHttpClient = asyncHttpClient

        # 服务对象缓存
        self.__serviceCache = {}

        # 不指定服务中心配置时使用默认配置
        if self.centerConfig == None:
            self.centerConfig = {
                'host': '127.0.0.1',
                'port': 21428,
                'transmissionType': None,
                'transmissionData': None
            }

    def __initCall(
            self, 
            serviceName: str
    ) -> OneCallProxy:
        '''
        服务调用前的初始化操作

        Args:
            serviceName: 服务名称
        '''
        serviceName = serviceName.strip()
        if not serviceName:
            errorMessage = f'The service name cannot be empty, please use the "serviceName" parameter to specify the service to be called'
            raise ServiceCallError(errorMessage)

        if not serviceName in self.__serviceCache:
            self.__serviceCache[serviceName] = OneCallProxy(
                serviceName=serviceName,
                centerConfig=self.centerConfig,
                httpClient=self.httpClient,
                asyncHttpClient=self.asyncHttpClient
            )

    def call(self, serviceName: str, apiName: str, method: str, *args, **kwargs):
        '''
        调用远程服务(同步)

        Args:
            serviceName: 服务名称
            apiName: 服务的API名称
            method: API的HTTP调用方法
            *args, **kwargs: 接口参数
        '''
        self.__initCall(serviceName=serviceName)
        return self.__serviceCache[serviceName].call(apiName, method, *args, **kwargs)

    async def asyncCall(self, serviceName: str, apiName: str, method: str, *args, **kwargs):
        '''
        调用远程服务(异步)

        Args:
            serviceName: 服务名称
            apiName: 服务的API名称
            method: API的HTTP调用方法
            *args, **kwargs: 接口参数
        '''
        self.__initCall(serviceName=serviceName)
        return await self.__serviceCache[serviceName].asyncCall(apiName, method, *args, **kwargs)

    def get(self, serviceName: str):
        '''
        获取某个服务的代理实例

        Args:
            serviceName: 待获实例的服务名称
        '''


