import functools
import operator
from python_helper import ObjectHelper
from python_framework import Repository

from enumeration.ModelState import ModelState


MESSAGE_MODEL = 'message'
EMISSION_MODEL = 'emission'


@Repository()
class MemoryRepository:

    data = {}


    def existsMessageByQueueKeyAndMessageKey(self, queueKey, messageKey):
        return messageKey in self.getMessageQueue(queueKey)


    def findAllMessagesByStateIn(self, stateList):
        return [
            self.getMessage(queueKey, messageKey)
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getMessageKeyIterator(queueKey)
            if self.messageStateIn(queueKey, messageKey, stateList)
        ]


    def removeAllMessagesByStateIn(self, stateList):
        messageList = [
            self.popMessage(queueKey, messageKey)
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getMessageKeyIterator(queueKey)
            if self.messageStateIn(queueKey, messageKey, stateList)
        ]
        self.removeEmptyQueues()
        return messageList


    def removeAllMessagesByStateInAndSatusIn(self, stateList, statusList):
        messageList = [
            self.popMessage(queueKey, messageKey)
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getMessageKeyIterator(queueKey)
            if self.messageStateIn(queueKey, messageKey, stateList) and self.messageStatusIn(queueKey, messageKey, statusList)
        ]
        self.removeEmptyQueues()
        return messageList


    def findAllMessagesByStatusIn(self, statusList):
        return [
            self.getMessage(queueKey, messageKey)
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getMessageKeyIterator(queueKey)
            if self.messageStatusIn(queueKey, messageKey, statusList)
        ]


    def removeAllMessageByStatusIn(self, statusList):
        messageList = [
            self.popMessage(queueKey, messageKey)
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getMessageKeyIterator(queueKey)
            if self.messageStatusIn(queueKey, messageKey, statusList)
        ]
        self.removeEmptyQueues()
        return messageList


    def findAllMessagesByStatusInFromOneQueue(self, statusList):
        queueKeyList = self.getQueueKeyIterator()
        if ObjectHelper.isEmpty(queueKeyList):
            return []
        for queueKey in self.getQueueKeyIterator():
            messageList = [
                self.getMessage(queueKey, messageKey)
                for messageKey in self.getMessageKeyIterator(queueKey)
                if self.messageStatusIn(queueKey, messageKey, statusList)
            ]
            if 0 < len(messageList):
                return messageList
        return []


    def getMessageKeyIterator(self, queueKey):
        return [*self.getMessageQueue(queueKey).keys()]


    def getEmissionMessageKeyIterator(self, queueKey):
        return [*self.getEmissionQueue(queueKey).keys()]


    def getMessage(self, queueKey, messageKey):
        return self.getMessageQueue(queueKey).get(messageKey)


    def popMessage(self, queueKey, messageKey):
        return self.getMessageQueue(queueKey).pop(messageKey)


    def getMessageQueue(self, queueKey):
        return self.getQueue(queueKey).get(MESSAGE_MODEL, {})


    def getEmissionQueue(self, queueKey):
        return self.getQueue(queueKey).get(EMISSION_MODEL, {})


    def getEmissionList(self, queueKey, messageKey):
        return self.getEmissionQueue(queueKey).get(messageKey, [])


    def findAllEmissionsByStateIn(self, stateList):
        return [
            emission
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getEmissionMessageKeyIterator(queueKey)
            for emission in self.getEmissionList(queueKey, messageKey)
            if self.emissionStateIn(emission, stateList)
        ]


    def findAllEmissionsByStatusInFromOneQueue(self, statusList):
        queueKeyList = self.getQueueKeyIterator()
        if ObjectHelper.isEmpty(queueKeyList):
            return []
        for queueKey in queueKeyList:
            emissionList = [
                emission
                for messageKey in self.getMessageKeyIterator(queueKey)
                for emission in self.getEmissionList(queueKey, messageKey)
                if self.emissionStatusIn(emission, statusList)
            ]
            if 0 < len(emissionList):
                return emissionList
        return []


    def removeAllEmissionsByStateInAndSatusIn(self, stateList, statusList):
        emissionList = [
            self.popEmission(emission)
            for queueKey in self.getQueueKeyIterator()
            for messageKey in self.getEmissionMessageKeyIterator(queueKey)
            for emission in self.getEmissionList(queueKey, messageKey)
            if self.emissionStateIn(emission, stateList) and self.emissionStatusIn(emission, statusList)
        ]
        self.removeEmptyQueues()
        return emissionList


    def removeEmptyQueues(self):
        for queueKey in self.getQueueKeyIterator():
            if ObjectHelper.isEmpty(self.getMessageQueue(queueKey)) and ObjectHelper.isEmpty(self.getEmissionQueue(queueKey)):
                ObjectHelper.deleteDictionaryEntry(queueKey, self.data)


    def emissionStatusIn(self, emission, statusList):
        return ObjectHelper.isNotNone(emission) and emission.status in statusList


    def emissionStateIn(self, emission, stateList):
        return ObjectHelper.isNotNone(emission) and emission.state in stateList


    def popEmission(self, emission):
        emissionList = self.getEmissionQueue(emission.queueKey).get(emission.getMessageKey())
        emissionIndex = [
            i
            for i, e in enumerate(emissionList)
            if e == emission
        ]
        if ObjectHelper.isEmpty(emissionIndex):
            raise Exception(f'Emission {emission} not found')
        if 1 == len(emissionList):
            self.getEmissionQueue(emission.queueKey).pop(emission.getMessageKey())
        else:
            self.getEmissionQueue(emission.queueKey).get(emission.getMessageKey()).pop(emissionIndex[0])
        return emission


    def messageStateIn(self, queueKey, messageKey, stateList):
        return ObjectHelper.isNotNone(self.getMessage(queueKey, messageKey)) and self.getMessage(queueKey, messageKey).state in stateList


    def messageStatusIn(self, queueKey, messageKey, statusList):
        return ObjectHelper.isNotNone(self.getMessage(queueKey, messageKey)) and self.getMessage(queueKey, messageKey).status in statusList


    def acceptMessage(self, message):
        self.addQueueKeyIfNeeded(message.queueKey)
        self.data[message.queueKey][MESSAGE_MODEL][message.key] = message
        return message


    def acceptEmissionList(self, emissionList, queue):
        if ObjectHelper.isNotEmpty(emissionList):
            message = emissionList[0].message
            self.addQueueKeyIfNeeded(queue.key)
            self.data[queue.key][EMISSION_MODEL][message.key] = emissionList


    def addQueueKeyIfNeeded(self, queueKey):
        if queueKey not in self.data:
            self.data[queueKey] = {
                MESSAGE_MODEL: {},
                EMISSION_MODEL: {}
            }


    def getQueueKeyIterator(self):
        return [*{**self.data}.keys()]


    def getQueue(self, queueKey):
        return self.data.get(queueKey, {})


    def findAll(self):
        return {**self.data}
