class ConnectivityException(Exception):
    pass


class VLANHandlerException(ConnectivityException):
    pass


class RequestValidatorException(ConnectivityException):
    pass


class ApplyConnectivityException(ConnectivityException):
    pass
