from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import QueueDto
from SubscriptionModel import SubscriptionModel

@Validator()
class QueueModelValidator:

    @ValidatorMethod(requestClass=[QueueDto.QueueRequestDto])
    def validateRequestDto(self, dto):
        if ObjectHelper.isNone(dto) or ObjectHelper.isNone(dto.key):
            raise GlobalException(
                message = f'Queue key cannot be None',
                logMessage = f'Subscription: {dto}',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[QueueDto.QueueRequestDto])
    def validateDoesNotExists(self, dto):
        self.validateRequestDto(dto)
        if self.service.queueModel.existsByKey(dto.key):
            raise GlobalException(
                message = f'Queue aleady exists',
                logMessage = f'Queue {dto.key} aleady exists',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[str])
    def validateExistsByKey(self, key):
        if not self.service.queueModel.existsByKey(key):
            raise GlobalException(
                message = 'Queue does not exists',
                logMessage = f'Queue {key} does not exists',
                status = HttpStatus.BAD_REQUEST
            )
