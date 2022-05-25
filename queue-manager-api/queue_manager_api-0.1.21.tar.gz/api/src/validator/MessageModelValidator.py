from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import MessageDto


@Validator()
class MessageModelValidator:

    @ValidatorMethod(requestClass=[MessageDto.MessageRequestDto])
    def validateRequestDto(self, dto):
        if ObjectHelper.isNone(dto) or ObjectHelper.isNone(dto.key):
            raise GlobalException(
                message = f'Message key cannot be None',
                logMessage = f'Subscription: {dto}',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[MessageDto.MessageRequestDto])
    def validateDoesNotExists(self, dto):
        self.validateRequestDto(dto)
        self.validateDoesNotExistsByKey(dto.key)


    @ValidatorMethod(requestClass=[str])
    def validateDoesNotExistsByKey(self, key):
        if ObjectHelper.isNone(key) or self.service.messageModel.existsByKey(key):
            raise GlobalException(
                message = 'Message aleady exists',
                logMessage = f'Message {key} aleady exists',
                status = HttpStatus.BAD_REQUEST
            )
