from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import ConverterStatic, Serializer
from python_framework import SqlAlchemyProxy as sap

from ModelAssociation import MESSAGE, EMISSION, MODEL
from constant import ModelConstant
from util import ModelUtil


class MessageModel(MODEL):
    __tablename__ = MESSAGE

    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    key = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False, unique=True)
    queueKey = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False)
    groupKey = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False)
    originKey = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False)
    content = sap.Column(sap.String(65_536))
    status = sap.Column(sap.String(sap.LITTLE_STRING_SIZE), nullable=False, default=ModelConstant.DEFAULT_STATUS)
    state = sap.Column(sap.String(sap.LITTLE_STRING_SIZE), nullable=False, default=ModelConstant.DEFAULT_STATE)

    history = sap.Column(sap.String(65_536))

    createdAt = sap.Column(sap.DateTime, nullable=False)
    updatedAt = sap.Column(sap.DateTime, nullable=False)


    def __init__(self,
        id = None,
        key = None,
        queueKey = None,
        groupKey = None,
        originKey = None,
        content = None,
        status = None,
        state = None,
        emissionList = None,
        history = None,
        createdAt = None,
        updatedAt = None
    ):
        self.id = id
        self.key = key
        self.queueKey = queueKey
        self.groupKey = groupKey
        self.originKey = originKey
        self.content = Serializer.jsonifyIt(content)
        self.status = ConverterStatic.getValueOrDefault(status, ModelConstant.DEFAULT_STATUS)
        self.state = ConverterStatic.getValueOrDefault(state, ModelConstant.DEFAULT_STATE)
        self.setHistory(history) ###- ModelUtil.getOneToManyData(history)

        self.createdAt = createdAt
        self.updatedAt = updatedAt
        ConverterStatic.overrideDateData(self)


    def setHistory(self, history):
        self.history = str(history)


    def addHistory(self, history):
        self.history = str(history)


    def __repr__(self):
        return f'{self.__tablename__}(id={self.id}, key={self.key}, queueKey={self.queueKey}, status={self.status}, state={self.state})'
