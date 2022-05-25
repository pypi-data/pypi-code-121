from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import Mapper, MapperMethod, ConverterStatic


from constant import SubscriptionConstant
import SubscriptionDto
import SubscriptionModel


@Mapper()
class SubscriptionModelMapper:

    @MapperMethod(requestClass=[[SubscriptionDto.SubscriptionRequestDto], str], responseClass=[[SubscriptionModel.SubscriptionModel]])
    def fromRequestDtoListToModelList(self, dtoList, modelList):
        self.overrideAllModelOriginKey(originKey, modelList)
        return modelList


    @MapperMethod(requestClass=[[SubscriptionModel.SubscriptionModel]], responseClass=[[SubscriptionDto.SubscriptionResponseDto]])
    def fromModelListToResponseDtoList(self, modelList, dtoList):
        return dtoList


    @MapperMethod(requestClass=[SubscriptionDto.SubscriptionRequestDto, str], responseClass=[SubscriptionModel.SubscriptionModel])
    def fromRequestDtoToModel(self, dto, originKey, model):
        self.overrideModelOriginKey(originKey, model)
        return model


    @MapperMethod(requestClass=[SubscriptionModel.SubscriptionModel], responseClass=[SubscriptionDto.SubscriptionResponseDto])
    def fromModelToResponseDto(self, model, dto):
        return dto


    @MapperMethod(requestClass=[SubscriptionModel.SubscriptionModel, SubscriptionDto.SubscriptionRequestDto])
    def overrideModel(self, model, dto):
        model.url = ConverterStatic.getValueOrDefault(dto.url, model.url)
        model.onErrorUrl = ConverterStatic.getValueOrDefault(dto.onErrorUrl, model.onErrorUrl)
        model.maxTries = ConverterStatic.getValueOrDefault(dto.maxTries, model.maxTries)
        model.backOff = ConverterStatic.getValueOrDefault(dto.backOff, model.backOff)


    @MapperMethod(requestClass=[str, SubscriptionModel.SubscriptionModel])
    def overrideModelOriginKey(self, originKey, model):
        model.originKey = ConverterStatic.getValueOrDefault(originKey, model.originKey)


    @MapperMethod(requestClass=[str, [SubscriptionModel.SubscriptionModel]])
    def overrideAllModelOriginKey(self, originKey, modelList):
        for model in modelList:
            self.overrideModelOriginKey(originKey, model)
