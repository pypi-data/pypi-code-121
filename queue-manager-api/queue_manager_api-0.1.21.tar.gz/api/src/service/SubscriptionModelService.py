from python_helper import ObjectHelper
from python_framework import Service, ServiceMethod, GlobalException

from util import AuditoryUtil
import SubscriptionDto


@Service()
class SubscriptionModelService:

    @ServiceMethod()
    def findAllByOrigin(self):
        return self.mapper.subscriptionModel.fromModelListToResponseDtoList(
            self.repository.subscriptionModel.findAllByOriginKey(AuditoryUtil.getApiKeyIdentity(service=self))
        )


    @ServiceMethod(requestClass=[SubscriptionDto.SubscriptionRequestDto])
    def createOrUpdate(self, dto):
        raise GlobalException(message='Method not implemented', status=HttpStatus.I_M_A_TEAPOT)


    @ServiceMethod(requestClass=[str])
    def findAllModelByQueueKey(self, queueKey):
        modelList = self.repository.subscriptionModel.findAllByQueueKey(queueKey)
        self.validator.subscriptionModel.validateIsAtLeastOne(modelList, queueKey)
        return modelList


    @ServiceMethod(requestClass=[[str]])
    def findAllModelByQueueKeyIn(self, queueKeyList):
        raise Exception('You should never make such a question')


    @ServiceMethod(requestClass=[str])
    def existsByKey(self, key):
        return self.repository.message.existsByKey(key)


    @ServiceMethod(requestClass=[str])
    def findModelByKey(self, key):
        modelList = self.findAllModelByKey(key)
        self.validator.queueModel.validateIsExactlyOne(modelList)
        return modelList[0]


    @ServiceMethod(requestClass=[str])
    def findAllModelByKey(self, key):
        return self.repository.subscriptionModel.findAllByKey(key)
