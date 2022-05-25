from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import SubscriptionDto
import SubscriptionModel

@Validator()
class SubscriptionModelValidator:

    @ValidatorMethod(requestClass=[SubscriptionDto.SubscriptionRequestDto])
    def validateRequestDto(self, dto):
        if ObjectHelper.isNone(dto) or ObjectHelper.isNone(dto.key):
            raise GlobalException(
                message = f'Subscription key cannot be None',
                logMessage = f'Subscription: {dto}',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[SubscriptionDto.SubscriptionRequestDto])
    def validateDoesNotExists(self, dto):
        self.validateRequestDto(dto)
        if self.service.queueModel.existsByKey(dto.key):
            raise GlobalException(
                message = 'Subscription aleady exists',
                logMessage = f'Subscription {dto.key} aleady exists',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[[SubscriptionModel.SubscriptionModel], str])
    def validateIsAtLeastOne(self, modelList, queueKey):
        if ObjectHelper.isEmpty(modelList):
            raise GlobalException(
                message = f'There are no subscriptions listenning to this queue: {queueKey}. Subscriptions: {modelList}',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[[SubscriptionModel.SubscriptionModel]])
    def validateIsExactlyOne(self, modelList):
        if ObjectHelper.isEmpty(modelList):
            raise GlobalException(
                message = 'Subscription not found',
                logMessage = f'An empty list of subscriptions was given: {modelList}',
                status = HttpStatus.BAD_REQUEST
            )
        if 1 < len(modelList):
            raise GlobalException(
                logMessage = f'There are more than one subscription with the same key: {modelList}',
                status = HttpStatus.INTERNAL_SERVER_ERROR
            )
