import os.path
from typing import Callable

from fastapi.routing import APIRoute
from fastapi import Request, Response

from mfhm.utils import generateServiceKey
from mfhm.service import BasicServices, SubService
from mfhm.errors import WrapperError
from mfhm.metadata import TransmissionType, TransmissionTypeField


class KeyAuth(object):
    '''
    服务密钥包装器, 包装后的服务将启用服务密钥验证
    '''
  
    def __new__(cls: type, serviceClass: BasicServices, *args, **kwargs) -> BasicServices:

        class RouteHandler(APIRoute):
            '''
            API路由处理类, 拦截请求并校验服务密钥
            '''
            serviceKey = None

            def get_route_handler(self) -> Callable:
                # 原始路由处理函数
                originalRouteHandler = super().get_route_handler()

                # 对每个请求做密钥校验
                async def customRouteHandler(request: Request) -> Response:
                    # 从请求头获取请求密钥
                    mfhmAuthKey = request.headers.get(
                        TransmissionTypeField.headers.get(TransmissionType.authKey)
                    )

                    if mfhmAuthKey:
                        if mfhmAuthKey == self.__class__.serviceKey:
                            return await originalRouteHandler(request)
                    # 校验失败返回403
                    return Response(
                        status_code=403,
                        content=f"You don't have permission to access service"
                    )

                return customRouteHandler
        
        service = serviceClass(*args, **kwargs)

        # 确保服务中已指定数据目录
        if not service.dataDir:
            raise WrapperError(
                f'To use the wrapper "{cls.__name__}" , the "dataDir" parameter needs \
                to be specified in the service "{service.__class__.__name__}"')

        # 初始化服务密钥
        keyFilePath = os.path.join(service.dataDir, 'key')
        try:
            # 如果存在本地密钥文件, 从密钥文件中读取密钥初始化
            if os.path.isfile(keyFilePath):
                with open(keyFilePath, 'r') as f:
                    RouteHandler.serviceKey = f.read().strip()
            # 否则生成新的服务密钥
            else:
                RouteHandler.serviceKey = generateServiceKey()
                with open(keyFilePath, 'w') as f:
                    f.write(RouteHandler.serviceKey)
        except Exception as err:
            raise WrapperError(f'Unable to read and write file: {keyFilePath}')

        # 为服务指定传输类型和传输相关凭证数据
        service.transmissionType = 'key'
        service.transmissionData = RouteHandler.serviceKey

        # 为服务指定API路由处理类
        # 子服务的路由处理类是 .route_class, 与服务本身的路由处理类有所区别
        if issubclass(serviceClass, SubService):
            service.route_class = RouteHandler
        else:
            service.router.route_class = RouteHandler

        return service



