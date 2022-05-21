from python_framework import ConverterStatic

from constant import EmissionConstant


class EmissionRequestDto:
    def __init__(self,
        queueKey = None,
        subscriptionKey = None,
        url = None,
        tries = None,
        onErrorUrl = None,
        onErrorTries = None,
        maxTries = None,
        backOff = None,
        message = None
    ):
        self.queueKey = queueKey
        self.subscriptionKey = subscriptionKey
        self.url = url
        self.tries = ConverterStatic.getValueOrDefault(tries, EmissionConstant.ZERO_TRIES)
        self.onErrorUrl = onErrorUrl
        self.onErrorTries = ConverterStatic.getValueOrDefault(onErrorTries, EmissionConstant.ZERO_TRIES)
        self.maxTries = ConverterStatic.getValueOrDefault(maxTries, EmissionConstant.DEFAULT_MAX_TRIES)
        self.backOff = ConverterStatic.getValueOrDefault(backOff, EmissionConstant.DEFAULT_BACKOFF)
        self.message = message


class EmissionResponseDto:
    def __init__(self,
        queueKey = None,
        subscriptionKey = None,
        url = None,
        tries = None,
        onErrorUrl = None,
        onErrorTries = None,
        maxTries = None,
        backOff = None,
        message = None,
        history = None
    ):
        self.queueKey = queueKey
        self.subscriptionKey = subscriptionKey
        self.url = url
        self.tries = ConverterStatic.getValueOrDefault(tries, EmissionConstant.ZERO_TRIES)
        self.onErrorUrl = onErrorUrl
        self.onErrorTries = ConverterStatic.getValueOrDefault(onErrorTries, EmissionConstant.ZERO_TRIES)
        self.maxTries = ConverterStatic.getValueOrDefault(maxTries, EmissionConstant.DEFAULT_MAX_TRIES)
        self.backOff = ConverterStatic.getValueOrDefault(backOff, EmissionConstant.DEFAULT_BACKOFF)
        self.message = message
        self.history = ConverterStatic.getValueOrDefault(history, [])
