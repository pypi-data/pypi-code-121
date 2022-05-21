from python_framework import ConverterStatic


class QueueRequestDto:
    def __init__(self,
        key = None,
        subscriptionList = None
    ):
        self.key = key
        self.subscriptionList = ConverterStatic.getValueOrDefault(subscriptionList, [])


class QueueResponseDto:
    def __init__(self,
        key = None,
        subscriptionList = None
    ):
        self.key = key
        self.subscriptionList = ConverterStatic.getValueOrDefault(subscriptionList, [])
