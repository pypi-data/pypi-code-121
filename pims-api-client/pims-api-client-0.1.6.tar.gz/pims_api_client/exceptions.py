import httpx


class HttpBaseException(Exception):
    def __init__(self, original_exception, message=None):
        self.message = message
        self.original_exception = original_exception
        super().__init__()

    def __str__(self):
        return self.message


class HttpConnectionFailed(HttpBaseException):
    pass


class HttpRequestError(HttpBaseException):
    pass


class HttpApiBaseException(HttpBaseException):
    def __init__(self, original_exception, message=None):
        self.status_code = original_exception.response.status_code
        super().__init__(original_exception=original_exception, message=message)

    def __str__(self):
        return f'{self.status_code}:{self.message}'


class Api4xxException(HttpApiBaseException):
    pass


class Api5xxException(HttpApiBaseException):
    pass


class Api404Exception(Api4xxException):
    pass


class Api401Exception(Api4xxException):
    pass


class Api400Exception(Api4xxException):
    pass


class Api500Exception(Api5xxException):
    pass


def raise_the_desired_api_error(exception: httpx.HTTPStatusError):
    if exception.response.status_code == 404:
        raise Api404Exception(exception, message="404 не найдено")
    elif exception.response.status_code == 401:
        raise Api401Exception(exception, message="срок действия токена истек")
    elif exception.response.status_code == 400:
        raise Api400Exception(exception, message=exception.response.json()['message'])
    elif exception.response.status_code in range(400, 499):
        raise Api4xxException(exception, message="4хх ошибка")
    elif exception.response.status_code == 500:
        raise Api500Exception(exception)
    elif exception.response.status_code > 500:
        raise Api5xxException(exception)


def method_catches_httpx_request_error(cor): 
    '''
        декоратор для асинхронного метода (корутины) cor, 
        работающего через httpxClient,
        при возникновении ошибки httpx.RequestError
        вызывает HttpRequestError
    '''
    
    async def wrapper(self, *args, **kwargs):
        try:
            return await cor(self, *args, **kwargs)
        except httpx.RequestError as exc:
            raise HttpRequestError(exc, message=str(exc)) 
            
    return wrapper