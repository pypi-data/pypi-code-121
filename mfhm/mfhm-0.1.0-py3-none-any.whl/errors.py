class PathError(Exception):
    '''
    路径错误
    '''


class OnlineError(Exception):
    '''
    服务上线错误
    '''


class ServiceStartError(Exception):
    '''
    服务启动失败
    '''


class ServiceCenterCommunicationError(Exception):
    '''
    与服务中心通信错误
    '''


class ServiceCallError(Exception):
    '''
    远程服务调用错误
    '''


class ParameterError(Exception):
    '''
    参数错误
    '''


class WrapperError(Exception):
    '''
    服务包装器错误
    '''


class ConfigError(Exception):
    '''
    配置错误
    '''


