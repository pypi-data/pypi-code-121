from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import Message, Emission, QueueModel


@Validator()
class MemoryValidator:

    @ValidatorMethod(requestClass=[Message.Message])
    def validateMessage(self, message):
        if ObjectHelper.isNone(message) or ObjectHelper.isNone(message.key) or ObjectHelper.isNone(message.queueKey):
            raise GlobalException(
                logMessage = f'Message key cannot be None. Message: {message}',
                status = HttpStatus.INTERNAL_SERVER_ERROR
            )


    @ValidatorMethod(requestClass=[Message.Message])
    def validateMessageDoesNotExists(self, message):
        self.validateMessage(message)
        if self.service.memory.messageExists(message):
            raise GlobalException(
                message = 'Message aleady in process',
                logMessage = f'Message "{message.key}" from subscription "{message.queueKey}" aleady in process',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[[Emission.Emission], QueueModel.QueueModel])
    def validateThereAreAtLeastOneEmission(self, emissionList, queue):
        if ObjectHelper.isEmpty(emissionList):
            raise GlobalException(
                message = 'There are no subscriptions for this queue',
                logMessage = f'There are no subscriptions for the "{queue.key}" queue',
                status = HttpStatus.BAD_REQUEST
            )
