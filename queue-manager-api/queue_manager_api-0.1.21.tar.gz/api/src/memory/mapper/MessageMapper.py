from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import Mapper, MapperMethod, EnumItem

import Message
import MessageDto
from enumeration.ModelState import ModelState
from enumeration.ModelStatus import ModelStatus


@Mapper()
class MessageMapper:

    @MapperMethod(requestClass=[Message.Message], responseClass=[MessageDto.MessageCreationResponseDto])
    def fromModelToCreationResponseDto(self, model, dto):
        return dto


    @MapperMethod(requestClass=[[MessageDto.MessageRequestDto], str], responseClass=[[Message.Message]])
    def fromRequestDtoListToModelList(self, dtoList, originKey, modelList):
        for model in modelList:
            self.handleInitializationSpecialCases(originKey, model)
        return modelList


    @MapperMethod(requestClass=[[Message.Message]], responseClass=[[MessageDto.MessageResponseDto]])
    def fromModelListToResponseDtoList(self, modelList, dtoList):
        return dtoList


    @MapperMethod(requestClass=[MessageDto.MessageRequestDto, str], responseClass=[Message.Message])
    def fromRequestDtoToModel(self, dto, originKey, model):
        self.handleInitializationSpecialCases(originKey, model)
        return model


    @MapperMethod(requestClass=[Message.Message], responseClass=[MessageDto.MessageResponseDto])
    def fromModelToResponseDto(self, model, dto):
        return dto


    @MapperMethod(requestClass=[Message.Message, EnumItem])
    def overrideModelState(self, model, state):
        model.state = state


    @MapperMethod(requestClass=[[Message.Message], EnumItem])
    def overrideAllModelState(self, modelList, state):
        for model in modelList:
            self.overrideModelState(model, state)


    @MapperMethod(requestClass=[Message.Message, EnumItem])
    def overrideModelStatus(self, model, status):
        model.status = status
        self.overrideModelStateToModified(model)


    @MapperMethod(requestClass=[[Message.Message], EnumItem])
    def overrideAllModelStatus(self, modelList, status):
        for model in modelList:
            self.overrideModelStatus(model, status)


    @MapperMethod(requestClass=[Message.Message])
    def overrideModelStateToModified(self, model):
        if ModelStatus.ACCEPTED == model.status:
            self.mapper.message.overrideModelState(model, ModelState.INSTANTIATED)
        else:
            self.mapper.message.overrideModelState(model, ModelState.MODIFIED)


    @MapperMethod(requestClass=[str, Message.Message])
    def overrideModelOriginKey(self, originKey, model):
        model.originKey = originKey


    @MapperMethod(requestClass=[Message.Message])
    def overrideModelGroupKey(self, model):
        if ObjectHelper.isNone(model.groupKey):
            model.groupKey = model.key


    @MapperMethod(requestClass=[str, Message.Message])
    def handleInitializationSpecialCases(self, originKey, model):
        self.overrideModelStateToModified(model)
        self.overrideModelOriginKey(originKey, model)
        self.overrideModelGroupKey(model)
