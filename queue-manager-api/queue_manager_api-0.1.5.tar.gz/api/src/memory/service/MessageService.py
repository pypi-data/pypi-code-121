from python_helper import log, ObjectHelper
from python_framework import Service, ServiceMethod

import MessageDto
import Message
from enumeration.ModelStatus import ModelStatus
from enumeration.ModelState import ModelState
from util import AuditoryUtil


LOG_LEVEL = log.STATUS


@Service()
class MessageService:

    @ServiceMethod(requestClass=[MessageDto.MessageRequestDto])
    def accept(self, dto):
        self.validator.messageModel.validateDoesNotExists(dto)
        model = self.mapper.message.fromRequestDtoToModel(dto, AuditoryUtil.getApiKeyIdentity(service=self))
        self.mapper.message.overrideModelStatus(model, ModelStatus.ACCEPTED)
        log.prettyPython(self.accept, f'Accepting new queued message', model, logLevel=LOG_LEVEL)
        return self.mapper.message.fromModelToCreationResponseDto(self.service.memory.acceptMessage(model))


    @ServiceMethod()
    def sendAllAcceptedFromOneQueue(self):
        modelList = self.service.memory.getAllAcceptedMessagesFromOneQueue()
        if ObjectHelper.isEmpty(modelList):
            return []
        self.mapper.message.overrideAllModelStatus(modelList, ModelStatus.PROCESSING)
        log.prettyPython(self.sendAllAcceptedFromOneQueue, f'Processing queued messages', modelList, logLevel=LOG_LEVEL)
        try:
            self.validator.message.validateAllBelongsToTheSameQueue(modelList)
            queue = self.service.queueModel.findModelByKey(modelList[0].queueKey)
            self.service.emission.acceptWithoutValidation(modelList, queue)
            self.mapper.message.overrideAllModelStatus(modelList, ModelStatus.PROCESSED)
        except Exception as exception:
            self.mapper.message.overrideAllModelStatus(modelList, ModelStatus.PROCESSED_WITH_ERRORS)
            for model in modelList:
                model.addHistory(exception)
            raise exception


    @ServiceMethod()
    def updateAllModifiedFromMemory(self):
        modelList = self.service.memory.getAllModifiedMessages()
        return self.service.messageModel.createOrUpdateAll(modelList)
