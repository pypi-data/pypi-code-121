import time
from python_helper import log, ObjectHelper
from python_framework import Service, ServiceMethod

from constant import EmissionConstant
from enumeration.ModelState import ModelState
from enumeration.ModelStatus import ModelStatus

import MessageDto
import Emission, Message, SubscriptionModel, QueueModel


LOG_LEVEL = log.STATUS


@Service()
class EmissionService:

    @ServiceMethod(requestClass=[Message.Message, SubscriptionModel.SubscriptionModel, QueueModel.QueueModel])
    def buildNewModel(self, message, subscription, queue):
        model = Emission.Emission(
            queueKey = queue.key,
            subscriptionKey = subscription.key,
            url = subscription.url,
            tries = EmissionConstant.ZERO_TRIES,
            onErrorUrl = subscription.onErrorUrl,
            onErrorTries = EmissionConstant.ZERO_TRIES,
            maxTries = subscription.maxTries,
            backOff = subscription.backOff,
            state = ModelState.INSTANTIATED,
            message = message
        )
        message.emissionList.append(model)
        return model


    @ServiceMethod(requestClass=[Message.Message, QueueModel.QueueModel])
    def buildNewModelList(self, message, queue):
        return [
            self.buildNewModel(
                message,
                subscription,
                queue
            ) for subscription in queue.subscriptionList
        ]


    @ServiceMethod(requestClass=[[Message.Message], QueueModel.QueueModel])
    def acceptWithoutValidation(self, messageList, queue):
        for message in messageList:
            modelList = self.service.emission.buildNewModelList(message, queue)
            self.mapper.emission.overrideAllModelStatus(modelList, ModelStatus.ACCEPTED)
            log.prettyPython(self.acceptWithoutValidation, f'Accepting new queued message emissions', modelList, logLevel=LOG_LEVEL)
            self.service.memory.acceptEmissionList(modelList, queue)


    @ServiceMethod()
    def sendAllAcceptedFromOneQueue(self):
        modelList = self.service.memory.getAcceptedEmissionsFromOneQueue()
        if ObjectHelper.isEmpty(modelList):
            return []
        self.mapper.emission.overrideAllModelStatus(modelList, ModelStatus.PROCESSING)
        log.prettyPython(self.sendAllAcceptedFromOneQueue, f'Processing queued message emissions', modelList, logLevel=LOG_LEVEL)
        self.validator.emission.validateAllBelongsToTheSameQueue(modelList)
        for model in modelList:
            self.sendInAThread(model)


    @ServiceMethod(requestClass=[Emission.Emission])
    def sendInAThread(self, model):
        self.globals.api.queueManager.runInAThread(self.send, model)


    @ServiceMethod(requestClass=[Emission.Emission])
    def send(self, model):
        log.prettyPython(self.send, f'Sending queued message emission', model, logLevel=LOG_LEVEL)
        try:
            self.mapper.emission.overrideModelState(model, ModelState.MODIFIED)
            messageRequestDto = MessageDto.MessageRequestDto(
                key = model.getMessageKey(),
                queueKey = model.queueKey,
                groupKey = model.getGroupKey(),
                content = model.getContent()
            )
            emissionResponse = None
            if model.maxTries > model.tries:
                model.tries += 1
                emissionResponse = self.sendToDestiny(model.url, model.getHeaders(), messageRequestDto)
                self.mapper.emission.overrideModelStatus(model, ModelStatus.PROCESSED)
            elif ObjectHelper.isNeitherNoneNorBlank(model.onErrorUrl):
                model.onErrorTries += 1
                emissionResponse = self.sendToDestiny(model.onErrorUrl, model.getHeaders(), messageRequestDto)
                self.mapper.emission.overrideModelStatus(model, ModelStatus.PROCESSED_WITH_ERRORS)
            return emissionResponse
        except Exception as exception:
            time.sleep(model.backOff)
            model.addHistory(exception)
            if (
                model.maxTries > model.tries and ObjectHelper.isNoneOrBlank(model.onErrorUrl)
            ) or (
                model.maxTries > model.onErrorTries and ObjectHelper.isNeitherNoneNorBlank(model.onErrorUrl)
            ):
                log.warning(self.send, f'Error while trying to emit queued message emission "{model}". Going for another attempt', exception=exception, muteStackTrace=True)
                return self.send(model)
            else:
                self.mapper.emission.overrideModelStatus(model, ModelStatus.UNPROCESSED)
                log.failure(self.send, f'Queued message emission "{model}" processed with errors', exception=exception, muteStackTrace=True)
                return exception


    @ServiceMethod(requestClass=[str, dict, MessageDto.MessageRequestDto])
    def sendToDestiny(self, url, headers, messageRequestDto):
        return self.client.emission.send(url, messageRequestDto, headers=headers)


    @ServiceMethod()
    def updateAllModifiedFromMemory(self):
        modelList = self.service.memory.getAllModifiedEmissions()
        self.service.emissionModel.createOrUpdateAll(modelList)
