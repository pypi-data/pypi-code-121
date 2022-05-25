from python_helper import ObjectHelper
from python_framework import Mapper, MapperMethod

import QueueModel
import QueueDto


@Mapper()
class QueueModelMapper:

    @MapperMethod(requestClass=[[QueueDto.QueueRequestDto], str], responseClass=[[QueueModel.QueueModel]])
    def fromRequestDtoListToModelList(self, dtoList, originKey, modelList):
        for model in modelList:
            self.overrideModelOriginKey(originKey, model)
        return modelList


    @MapperMethod(requestClass=[[QueueModel.QueueModel]], responseClass=[[QueueDto.QueueResponseDto]])
    def fromModelListToResponseDtoList(self, modelList, dtoList):
        return dtoList


    @MapperMethod(requestClass=[QueueDto.QueueRequestDto, str], responseClass=[QueueModel.QueueModel])
    def fromRequestDtoToModel(self, dto, originKey, model):
        self.overrideModelOriginKey(originKey, model)
        return model


    @MapperMethod(requestClass=[QueueModel.QueueModel], responseClass=[QueueDto.QueueResponseDto])
    def fromModelToResponseDto(self, model, dto):
        return dto


    @MapperMethod(requestClass=[QueueModel.QueueModel, QueueDto.QueueRequestDto])
    def overrideModel(self, model, dto):
        subscriptionDictionary = {subscription.key: subscription for subscription in model.subscriptionList}
        for subscriptionDto in dto.subscriptionList:
            if subscriptionDto.key in subscriptionDictionary:
                self.mapper.subscriptionModel.overrideModel(
                    subscriptionDictionary.get(subscriptionDto.key),
                    subscriptionDto
                )
            else:
                model.subscriptionList.append(self.mapper.subscriptionModel.fromRequestDtoToModel(subscriptionDto, model.originKey))


    @MapperMethod(requestClass=[str, QueueModel.QueueModel])
    def overrideModelOriginKey(self, originKey, model):
        model.originKey = originKey
        self.mapper.subscriptionModel.overrideAllModelOriginKey(originKey, model.subscriptionList)
