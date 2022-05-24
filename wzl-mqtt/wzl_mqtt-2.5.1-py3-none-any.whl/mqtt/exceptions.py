class MQTTException(RuntimeError):
    def __init__(self, *args, **kwargs):
        RuntimeError.__init__(self, *args, **kwargs)


class SubscriptionError(MQTTException):
    def __init__(self, *args, **kwargs):
        MQTTException.__init__(self, *args, **kwargs)


class ConnectionError(MQTTException):
    def __init__(self, *args, **kwargs):
        MQTTException.__init__(self, *args, **kwargs)


class CallbackError(MQTTException):
    def __init__(self, *args, **kwargs):
        MQTTException.__init__(self, *args, **kwargs)


class PublishError(MQTTException):
    def __init__(self, *args, **kwargs):
        MQTTException.__init__(self, *args, **kwargs)
