from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import Mapper, MapperMethod, EnumItem, ConverterStatic

import MessageModel
import Message
from enumeration.ModelState import ModelState
from enumeration.ModelStatus import ModelStatus


@Mapper()
class MessageModelMapper:

    @MapperMethod(requestClass=[[Message.Message]], responseClass=[[MessageModel.MessageModel]])
    def fromRequestDtoListToModelList(self, dtoList, modelList):
        for model in modelList:
            self.handleInitializationSpecialCases(model)
        return modelList


    @MapperMethod(requestClass=[[MessageModel.MessageModel]], responseClass=[[Message.Message]])
    def fromModelListToResponseDtoList(self, modelList, dtoList):
        return dtoList


    @MapperMethod(requestClass=[Message.Message], responseClass=[MessageModel.MessageModel])
    def fromRequestDtoToModel(self, dto, model):
        self.handleInitializationSpecialCases(model)
        return model


    @MapperMethod(requestClass=[MessageModel.MessageModel], responseClass=[Message.Message])
    def fromModelToResponseDto(self, model, dto):
        return dto


    @MapperMethod(requestClass=[MessageModel.MessageModel, MessageModel.MessageModel])
    def overrideModel(self, modelToOverride, model):
        self.handleInitializationSpecialCases(modelToOverride)
        modelToOverride.status = model.status


    @MapperMethod(requestClass=[MessageModel.MessageModel, EnumItem])
    def overrideModelState(self, model, state):
        model.state = state
        ConverterStatic.overrideDateData(model)


    @MapperMethod(requestClass=[[MessageModel.MessageModel], EnumItem])
    def overrideAllModelState(self, modelList, state):
        for model in modelList:
            self.overrideModelState(model, state)


    @MapperMethod(requestClass=[MessageModel.MessageModel, EnumItem])
    def overrideModelStatus(self, model, status):
        self.handleInitializationSpecialCases(model)
        model.status = status


    @MapperMethod(requestClass=[[MessageModel.MessageModel], EnumItem])
    def overrideAllModelStatus(self, modelList, status):
        for model in modelList:
            self.overrideModelStatus(model, status)


    @MapperMethod(requestClass=[MessageModel.MessageModel])
    def overrideModelStateToModified(self, model):
        if ModelStatus.ACCEPTED == model.status:
            self.mapper.message.overrideModelState(model, ModelState.INSTANTIATED)
        else:
            self.mapper.message.overrideModelState(model, ModelState.MODIFIED)


    @MapperMethod(requestClass=[MessageModel.MessageModel])
    def overrideModelGroupKey(self, model):
        if ObjectHelper.isNone(model.groupKey):
            model.groupKey = model.key


    @MapperMethod(requestClass=[MessageModel.MessageModel])
    def handleInitializationSpecialCases(self, model):
        self.overrideModelStateToModified(model)
        self.overrideModelGroupKey(model)
