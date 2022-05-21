from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import SqlAlchemyProxy as sap
from python_framework import ConverterStatic

from ModelAssociation import SUBSCRIPTION, QUEUE, MODEL
from constant import SubscriptionConstant
from util import ModelUtil


class SubscriptionModel(MODEL):
    __tablename__ = SUBSCRIPTION

    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    key = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False, unique=True)
    originKey = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False)
    url = sap.Column(sap.String(sap.LARGE_STRING_SIZE), nullable=False)
    onErrorUrl = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE))
    maxTries = sap.Column(sap.Integer(), nullable=False, default=SubscriptionConstant.DEFAULT_MAX_TRIES)
    backOff = sap.Column(sap.Float(precision=3), nullable=False, default=SubscriptionConstant.DEFAULT_BACKOFF)

    queue, queueId = sap.getManyToOne(SUBSCRIPTION, QUEUE, MODEL)

    def __init__(self,
        id = None,
        key = None,
        originKey = None,
        url = None,
        onErrorUrl = None,
        maxTries = None,
        backOff = None,
        headers = None,
        queue = None,
        queueId = None
    ):
        self.id = id
        self.key = key
        self.originKey = originKey
        self.url = url
        self.onErrorUrl = onErrorUrl
        self.maxTries = ConverterStatic.getValueOrDefault(maxTries, SubscriptionConstant.DEFAULT_MAX_TRIES)
        self.backOff = ConverterStatic.getValueOrDefault(backOff, SubscriptionConstant.DEFAULT_BACKOFF)
        self.setQueue(queue, queueId=queueId)


    def getQueueKey(self):
        return None if ObjectHelper.isNone(self.queue) else self.queue.key


    def setQueue(self, queue, queueId=None):
        self.queue, self.queueId = ModelUtil.getManyToOneData(queue, queueId, MODEL)


    def __repr__(self):
        return f'{self.__tablename__}(id={self.id}, key={self.key}, queueKey={self.getQueueKey()}, originKey={self.originKey}, maxTries={self.maxTries}, backOff={self.backOff}, url={self.url}, onErrorUrl={self.onErrorUrl})'
