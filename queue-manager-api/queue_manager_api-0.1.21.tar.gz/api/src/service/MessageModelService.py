from python_helper import log, ObjectHelper
from python_framework import Service, ServiceMethod

import MessageDto
import MessageModel, Message, EmissionModel
from enumeration.ModelStatus import ModelStatus
from enumeration.ModelState import ModelState


LOG_LEVEL = log.STATUS


@Service()
class MessageModelService:

    @ServiceMethod(requestClass=[[Message.Message]])
    def createOrUpdateAll(self, messageList):
        if ObjectHelper.isEmpty(messageList):
            return []
        self.mapper.message.overrideAllModelState(messageList, ModelState.PERSISTED)
        modelList = self.mapper.messageModel.fromRequestDtoListToModelList(messageList)
        log.prettyPython(self.createOrUpdateAll, f'Creating or updating queued messages', modelList, logLevel=LOG_LEVEL)
        existingModelList = self.findAllModelByKeyIn(list({model.key for model in modelList}))
        existingModelDictionary = {
            model.key: model for model in existingModelList
        }
        for model in modelList:
            if model.key in existingModelDictionary:
                self.mapper.messageModel.overrideModel(
                    existingModelDictionary.get(model.key),
                    model
                )
            else:
                existingModelList.append(model)
        return self.persistAll(existingModelList)


    @ServiceMethod(requestClass=[Message.Message])
    def findOrCreateModel(self, model):
        existingModel = self.findByKey(model.key)
        if ObjectHelper.isNotNone(existingModel):
            return existingModel
        return self.persistAll([existingModel])[0]


    @ServiceMethod(requestClass=[str])
    def existsByKey(self, key):
        return self.repository.messageModel.existsByKey(key)


    @ServiceMethod(requestClass=[[str]])
    def findAllModelByKeyIn(self, modelKeyList):
        return self.repository.messageModel.findAllByKeyIn(modelKeyList)


    @ServiceMethod(requestClass=[[MessageModel.MessageModel]])
    def persistAll(self, modelList):
        self.mapper.messageModel.overrideAllModelState(modelList, ModelState.PERSISTED)
        log.prettyPython(self.createOrUpdateAll, f'Persisting queued messages', modelList, logLevel=LOG_LEVEL)
        return self.repository.messageModel.saveAll(modelList)
