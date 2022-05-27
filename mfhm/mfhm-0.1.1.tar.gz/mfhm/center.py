import threading
import asyncio
import os.path
import json
from os import getcwd
from time import sleep
from urllib.parse import urljoin
from typing import Dict, Union, List

from httpx import AsyncClient as asyncHttpClient
from fastapi import Request, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from mfhm.service import BasicServices
from mfhm.log import getLogger
from mfhm.metadata import TransmissionType, TransmissionTypeField


# -------------------------------------------------
# 服务上线参数校验模型
class ServiceOnlineMethodModel(BaseModel):
    path:str = Field(..., min_length=1, max_length=10240)
    methods:List[str]


class ServiceOnlineModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    port: int = Field(..., ge=1, le=65535)
    transmissionType: Union[None, str] = Field(..., min_length=1, max_length=1024)
    transmissionData: Union[None, str] = Field(..., min_length=1, max_length=10240)
    methods: Dict[str, ServiceOnlineMethodModel]

    @validator('transmissionType')
    def transmissionTypeWhitelistValidator(cls, value: Union[None, str]):
        if isinstance(value, str):
            whitelist = TransmissionType.all()
            value = value.strip()
            if not value in whitelist:
                raise ValueError(f'Transmission Type error, only allowed is {whitelist}')

        return value


class ServiceCenter(BasicServices):
    '''
    服务中心类, 一个实例代表一个服务中心
    '''
    def __init__(
            self, 
            serviceName: str = 'ServiceCenter', 
            serviceHost: str = '0.0.0.0', 
            servicePort: int = 21428, 
            pingTestInterval: int = 5,
            pingTestTimeout: int = 5,
            dataDir:str = os.path.join(getcwd(), 'data'),
            cacheSaveInterval: int = 120,
            asyncHttpClient: asyncHttpClient = asyncHttpClient(),
            logger = getLogger(os.path.basename(os.path.abspath(__file__))),
    ) -> None:
        '''
        Args:
            serviceName: 服务中心名称
            serviceHost: 服务主机地址(监听地址)
            servicePort: 服务端口(监听端口)
            pingTestInterval: ping测试间隔(单位:秒)
            pingTestTimeout: ping测试超时(单位: 秒), 该值不应该大于pingTestInterval
            dataDir: 数据存储目录
            cacheSaveInterval: 缓存保存间隔
            asyncHttpClient: HTTPX异步客户端
        '''
        self.dataDir = dataDir
        self.pingTestInterval = pingTestInterval
        self.pingTestTimeout = pingTestTimeout
        self.cacheSaveInterval = cacheSaveInterval
        self.asyncHttpClient = asyncHttpClient
        self.logger = logger
        self.__cache = {}
        super().__init__(
            serviceName=serviceName, 
            serviceHost=serviceHost, 
            servicePort=servicePort, 
            dataDir=dataDir, 
            asyncHttpClient=asyncHttpClient
        )

        # ping测试周期线程
        pingTestThread = threading.Thread(target=self.__startPeriodicPingTest, daemon=True)
        pingTestThread.start()

        # 载入本地缓存
        self.__loadCache()

        # 缓存周期保存线程
        cacheSaveThread = threading.Thread(target=self.__periodicSaveCache, daemon=True)
        cacheSaveThread.start()

        # 服务关闭时将缓存立即写入磁盘
        self.add_event_handler('shutdown', self.__saveCache)

    def __deleteService(self, name:str, host:str, port:int) -> bool:
        '''
        从缓存中删除一个服务信息

        Args:
            name: 服务名称
            host: 服务主机地址
            port: 服务端口
        '''
        name = name.strip()
        for serviceName in self.__cache:
            # 找到指定名称的服务
            if serviceName == name:
                # 找到主机地址和端口一致的服务信息
                for oneServiceData in self.__cache[serviceName]:
                    if oneServiceData['host'] == host and oneServiceData['port'] == port:
                        # 从缓存中移除改服务信息
                        self.__cache[serviceName].remove(oneServiceData)
                        return True
        return False

    def __startPeriodicPingTest(self):
        '''
        启动周期Ping测试
        '''
        asyncio.run(self.__periodicPingTest())

    async def __periodicPingTest(self):
        '''
        周期Ping测试
        '''
        while True:
            sleep(self.pingTestInterval)
            # 在循环中使用await等待时Python会将整个循环视为一个协程, 不能达到异步
            # 的目的, 需要创建任务后统一执行
            taskList = []
            for serviceName in self.__cache:
                for serviceData in self.__cache[serviceName]:
                    taskList.append(self.__onePingTest(serviceName, serviceData))

            await asyncio.gather(*taskList)
            
    async def __onePingTest(self, name:str, serviceData: dict) -> None:
        '''
        向单个被托管服务发送ping测试

        Args:
            name: 服务名称
            serviceData: 服务信息数据       
        '''
        host = serviceData['host']
        port = serviceData['port']
        headers = {}

        # 如果目标服务启用了传输认证
        if serviceData['transmissionType']:
            # 且传输认证类型是密钥验证
            if serviceData['transmissionType'] == TransmissionType.authKey:
                # 请求头中携带服务中心的传输验证密钥
                headers[TransmissionTypeField.headers.get(TransmissionType.authKey)] = serviceData['transmissionData']

        url = f'http://{host}:{port}/ping'
        try:
            response = await self.asyncHttpClient.get(url, headers=headers, timeout=self.pingTestTimeout)
            self.logger.debug(f'Ping test: [{name}]{url}')
        except Exception as err:
            # 测试失败时讲服务视为已掉线, 从缓存中移除服务数据
            self.__deleteService(name=name, host=host, port=port)
            self.logger.warning(f'ping test failed [{name}]{url}, remove service data: {err}')
            return None

        # 状态码非200时视为服务测试失败, 从缓存中移除服务数据
        if not response.status_code == 200:
            self.__deleteService(name=name, host=host, port=port)
            self.logger.warning(
                f'ping test failed [{name}]{url}, remove service data:\n\
                    HTTP Statu code: {response.status_code}\n\
                    Respon data: {response.content}')
            return None
        
        # 响应时长
        serviceData['ping'] = response.elapsed.total_seconds()

    def __periodicSaveCache(self) -> None:
        '''
        周期调用缓存保存方法将缓存保存到磁盘
        '''
        while True:
            self.__saveCache()
            sleep(self.cacheSaveInterval)

    def __saveCache(self) -> bool:
        '''
        将缓存保存到磁盘

        Args:
            saveDir: 保存目录的路径
            cacheFilename: 保存的文件名称

        Returns:
            True: 保存成功
            False: 保存失败
        '''
        saveFilePath = os.path.join(self.dataDir, 'centerCache.json')
        try:        
            with open(saveFilePath, 'w', encoding='utf-8') as f:
                json.dump(self.__cache, f)
        except Exception as err:
            self.logger.warning(f'Cache save failure, all service data lost after service restart/exit: {err}')
            return False

        return True

    def __loadCache(self) -> bool:
        '''
        从磁盘加载缓存
        '''
        cacheFilePath = os.path.join(self.dataDir, 'centerCache.json')
        if os.path.isfile(cacheFilePath):
            try:
                with open(cacheFilePath, 'r', encoding='utf-8') as f:
                    self.__cache = json.load(f)
                return True
            except Exception as err:
                self.logger.critical(f'Cache load failure: {err}')

        return False

    async def online(self, request:Request, serviceData: ServiceOnlineModel):
        '''
        服务上线接口
        '''
        result = {'code': 0, 'message': 'ok'}
        serviceData = serviceData.dict()
        serviceHost = request.client.host

        # 如果请求上线的服务已在缓存中存在同名服务
        serviceName = serviceData['name'].strip()
        if serviceName in self.__cache:
            # 通过服务地址和服务端口判断是否为同一个服务
            for cacheServiceData in self.__cache[serviceName]:
                if serviceHost == cacheServiceData['host'] and serviceData['port'] == cacheServiceData['port']:
                   result['code'] = -1
                   result['message'] = 'Service is online'
                   return result
        else:
            self.__cache[serviceName] = []

        # 上线成功, 向缓存中写入服务信息
        self.__cache[serviceName].append({
            'host': serviceHost,
            'port': serviceData['port'],
            'ping': -1,
            'transmissionType': serviceData['transmissionType'],
            'transmissionData': serviceData['transmissionData'],
            'methods': serviceData['methods']
        })

        return result 

    async def offline(
            self, 
            request:Request,
            name:str = Path(..., min_length=1, max_length=500), 
            port:int = Path(..., ge=1, le=65535)
    ):
        '''
        服务下线

        Args:
            request: 请求对象, 用于获取客户端的请求信息
            name: 待下线的服务名称
            port: 待下线的服务的端口

        Returns:
            HTTP Code 200: 请求处理成功, 返回一个JSON {'code': xx, 'message': 'xx'}
                code: 状态码
                     0: 服务下线成功
                    -1: 下线服务不存在
            HTTP Code 422: 请求参数错误
            HTTP Code 500: 服务内部错误
        '''
        result = {'code': 0, 'message': 'ok'}

        name = name.strip()
        host = request.client.host

        if not self.__deleteService(name=name, host=host, port=port):
            result['code'] = -1
            result['message'] = 'Service not online'

        return result

    async def serviceInfo(self, name:str = Path(..., min_length=1, max_length=500)):
        '''
        服务信息获取接口

        Returns:
            HTTP Code 404: 服务接口不存在, 返回一个包含错误信息的JSON
            HTTP Code 422: 请求参数错误
            HTTP Code 200: 请求处理成功, 返回一个包含接口信息的JSON
            HTTP Code 500: 服务内部错误
        '''
        result = {
            'code': 0, 
            'message': 'ok'
        }

        name = name.strip()

        if name in self.__cache:
            # 找到ping值最小的服务
            pingValue = None
            minPingValueServiceData = None

            for serviceData in self.__cache[name]:
                # 使用首个服务数据作为初始值
                if pingValue == None:
                    pingValue = serviceData['ping']
                    minPingValueServiceData = serviceData
                # 两个以上服务时进行ping值对比
                elif serviceData['ping'] < pingValue:
                    pingValue = serviceData['ping']
                    minPingValueServiceData = serviceData

            if minPingValueServiceData:
                result['name'] = name
                result['host'] = minPingValueServiceData['host']
                result['port'] = minPingValueServiceData['port']
                result['transmissionType'] = minPingValueServiceData['transmissionType']
                result['transmissionData'] = minPingValueServiceData['transmissionData']
                result['methods'] = minPingValueServiceData['methods']
                return result

        result['code'] = -1
        result['message'] = 'Service not online'
        return JSONResponse(
            status_code=404, 
            content=result
        )

    async def apiInfo(
            self,
            name:str = Path(..., min_length=1, max_length=500),
            apiName:str = Path(..., min_length=1, max_length=500)
    ):
        '''
        服务接口信息获取接口

        Returns:
            HTTP Code 404: 服务接口不存在, 返回一个包含错误信息的JSON
            HTTP Code 422: 请求参数错误
            HTTP Code 200: 请求处理成功, 返回一个包含接口信息的JSON
            HTTP Code 500: 服务内部错误
        '''
        result = {'code': 0, 'message': 'ok'}

        name = name.strip()
        apiName = apiName.strip()

        if name in self.__cache:
            # 找到ping值最小的服务
            pingValue = None
            minPingValueServiceData = None

            for serviceData in self.__cache[name]:
                # 使用首个服务数据作为初始值
                if pingValue == None:
                    pingValue = serviceData['ping']
                    minPingValueServiceData = serviceData
                # 两个以上服务时进行ping值对比
                elif serviceData['ping'] < pingValue:
                    pingValue = serviceData['ping']
                    minPingValueServiceData = serviceData

            # 从服务中查询API信息
            if minPingValueServiceData:
                for methodName in minPingValueServiceData['methods']:
                    if methodName == apiName:
                        apiPath = serviceData['methods'][methodName]['path']
                        result['apiUrl'] = urljoin(f'http://{serviceData["host"]}:{serviceData["port"]}', apiPath)
                        result['apiMethods'] = serviceData['methods'][methodName]['methods']
                        return result

                result['code'] = -1
                result['message'] = f'API "{apiName}" does not exist for the service "{name}"'
                return JSONResponse(
                    status_code=404, 
                    content=result
                )

        result['code'] = -1
        result['message'] = 'Service not online'
        return JSONResponse(
            status_code=404, 
            content=result
        )

    async def ping(self):
        return {'code': 0, 'message': 'ok'}

    def initApi(self):
        '''
        初始化API接口
        '''
        # 绑定路由处理函数
        self.add_api_route('/online', self.online, methods=['POST'], name='online')
        self.add_api_route('/offline/{name}/{port}', self.offline, methods=['DELETE'], name='offline')
        self.add_api_route('/service/{name}', self.serviceInfo, methods=['GET'], name='service')
        self.add_api_route('/api/{name}/{apiName}', self.apiInfo, methods=['GET'], name='api')
        self.add_api_route('/ping', self.ping, methods=['GET'], name='ping')
