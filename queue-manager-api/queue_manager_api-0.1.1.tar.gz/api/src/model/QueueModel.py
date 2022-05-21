from python_framework import SqlAlchemyProxy as sap

from ModelAssociation import QUEUE, SUBSCRIPTION, MODEL
from util import ModelUtil


class QueueModel(MODEL):
    __tablename__ = QUEUE

    id = sap.Column(sap.Integer(), sap.Sequence(f'{__tablename__}{sap.ID}{sap.SEQ}'), primary_key=True)
    key = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False, unique=True)
    originKey = sap.Column(sap.String(sap.MEDIUM_STRING_SIZE), nullable=False)

    subscriptionList = sap.getOneToMany(QUEUE, SUBSCRIPTION, MODEL)

    def __init__(self,
        id = None,
        key = None,
        originKey = None,
        subscriptionList = None
    ):
        self.id = id
        self.key = key
        self.originKey = originKey
        self.subscriptionList = ModelUtil.getOneToManyData(subscriptionList)


    def __repr__(self):
        return f'{self.__tablename__}(id={self.id}, key={self.key}, originKey={self.originKey}, subscriptionKeyList={[subscription.key for subscription in self.subscriptionList]})'
