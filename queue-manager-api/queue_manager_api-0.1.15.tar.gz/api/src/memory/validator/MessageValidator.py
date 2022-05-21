from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import MessageDto
import Message


@Validator()
class MessageValidator:

    @ValidatorMethod(requestClass=[MessageDto.MessageRequestDto])
    def validateRequestDto(self, dto):
        self.validator.messageModel.validateRequestDto(dto)


    @ValidatorMethod(requestClass=[MessageDto.MessageRequestDto])
    def validateDoesNotExists(self, dto):
        self.validator.messageModel.validateRequestDto(dto)


    @ValidatorMethod(requestClass=[[Message.Message]])
    def validateAllBelongsToTheSameQueue(self, modelList):
        if not 1 == len({model.queueKey for model in modelList if ObjectHelper.isNotNone(model.queueKey)}):
            raise GlobalException(
                logMessage = f'All messages should be from the same queue. Messages: {modelList}',
                status = HttpStatus.INTERNAL_SERVER_ERROR
            )
