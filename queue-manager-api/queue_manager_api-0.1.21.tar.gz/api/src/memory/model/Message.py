from python_helper import Constant as c
from python_helper import ObjectHelper
from python_framework import ConverterStatic, Serializer
from python_framework import SqlAlchemyProxy as sap

from ModelAssociation import MESSAGE, EMISSION
from constant import ModelConstant


class Message:
    __memoryname__ = MESSAGE.replace(Serializer.MODEL_SUFIX, c.BLANK)

    def __init__(self,
        key = None,
        queueKey = None,
        groupKey = None,
        originKey = None,
        headers = None,
        content = None,
        status = None,
        state = None,
        emissionList = None,
        history = None
    ):
        self.key = key
        self.queueKey = queueKey
        self.groupKey = groupKey
        self.originKey = originKey
        self.headers = headers
        self.content = content
        self.status = ConverterStatic.getValueOrDefault(status, ModelConstant.DEFAULT_STATUS)
        self.state = ConverterStatic.getValueOrDefault(state, ModelConstant.DEFAULT_STATE)
        self.setEmissionList(emissionList)
        self.setHistory(history)


    def setEmissionList(self, emissionList):
        self.emissionList = ConverterStatic.getValueOrDefault(emissionList, [])


    def addEmissionList(self, emissionList):
        for emission in emissionList:
            self.addEmission(emission)


    def addEmission(self, emission):
        if not EmissionModelHelperStatic.containsEmission(self.emissionList, emission):
            self.emissionList.append(emission)


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
        return f'{self.__memoryname__}(key={self.key}, queueKey={self.queueKey}, groupKey={self.groupKey}, originKey={self.originKey}, status={self.status}, state={self.state})'
