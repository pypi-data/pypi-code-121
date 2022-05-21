from python_helper import Constant as c
from python_helper import ObjectHelper
from python_framework import ConverterStatic, Serializer
from python_framework import SqlAlchemyProxy as sap

from ModelAssociation import EMISSION, MESSAGE
from constant import EmissionConstant, ModelConstant


class Emission:
    __memoryname__ = EMISSION.replace(Serializer.MODEL_SUFIX, c.BLANK)

    def __init__(self,
        queueKey = None,
        subscriptionKey = None,
        url = None,
        tries = None,
        onErrorUrl = None,
        onErrorTries = None,
        maxTries = None,
        backOff = None,
        status = None,
        state = None,
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
        self.status = ConverterStatic.getValueOrDefault(status, ModelConstant.DEFAULT_STATUS)
        self.state = ConverterStatic.getValueOrDefault(state, ModelConstant.DEFAULT_STATE)
        self.setMessage(message)
        self.setHistory(history)


    def setMessage(self, message):
        self.message = message


    def getMessage(self, message=None):
        if ObjectHelper.isNotNone(message):
            self.setMessage(message)
        return self.message


    def getMessageKey(self, message=None):
        self.getMessage(message=message)
        return None if ObjectHelper.isNone(self.message) else self.message.key


    def getGroupKey(self, message=None):
        self.getMessage(message=message)
        return None if ObjectHelper.isNone(self.message) else self.message.groupKey


    def getOriginKey(self, message=None):
        self.getMessage(message=message)
        return None if ObjectHelper.isNone(self.message) else self.message.originKey


    def getHeaders(self):
        return dict() if ObjectHelper.isNone(self.message) else ConverterStatic.getValueOrDefault(self.message.headers, dict())


    def getContent(self):
        return None if ObjectHelper.isNone(self.message) else self.message.content


    def setHistory(self, history):
        if ObjectHelper.isNone(history):
            self.history = []
        elif ObjectHelper.isNotList(history):
            self.history = [str(history)]
        else:
            self.history = [
                str(h) for h in ConverterStatic.getValueOrDefault(history, [])
            ]
        # self.history = []


    def addHistory(self, history):
        self.history.append(str(history))
        # self.history = []


    def __repr__(self):
        return f'{self.__memoryname__}(queueKey={self.queueKey}, subscriptionKey={self.subscriptionKey}, messageKey={self.getMessageKey()}, groupKey={self.getGroupKey()}, originKey={self.getOriginKey()}, tries={self.tries}, onErrorTries={self.onErrorTries}, maxTries={self.maxTries}, backOff={self.backOff}, status={self.status}, state={self.state})'
