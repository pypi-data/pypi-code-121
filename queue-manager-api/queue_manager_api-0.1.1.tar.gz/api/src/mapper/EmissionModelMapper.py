from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import Mapper, MapperMethod, EnumItem, ConverterStatic

import EmissionModel
import Emission
from enumeration.ModelState import ModelState
from enumeration.ModelStatus import ModelStatus


@Mapper()
class EmissionModelMapper:

    @MapperMethod(requestClass=[[Emission.Emission]], responseClass=[[EmissionModel.EmissionModel]])
    def fromRequestDtoListToModelList(self, dtoList, modelList):
        for model, dto in zip(modelList, dtoList):
            self.overrideMessageKey(model, dto)
        return modelList


    @MapperMethod(requestClass=[[EmissionModel.EmissionModel]], responseClass=[[Emission.Emission]])
    def fromModelListToResponseDtoList(self, modelList, dtoList):
        raise Exception('This shoud not be called due history raw implmentation')
        return dtoList


    @MapperMethod(requestClass=[Emission.Emission], responseClass=[EmissionModel.EmissionModel])
    def fromRequestDtoToModel(self, dto, model):
        self.overrideMessageKey(model, dto)
        return model


    @MapperMethod(requestClass=[EmissionModel.EmissionModel], responseClass=[Emission.Emission])
    def fromModelToResponseDto(self, model, dto):
        raise Exception('This shoud not be called due history raw implmentation')
        return dto


    @MapperMethod(requestClass=[EmissionModel.EmissionModel, Emission.Emission])
    def overrideMessageKey(self, toOverridemodel, emission):
        toOverridemodel.messageKey = emission.getMessageKey()
        toOverridemodel.groupKey = emission.getGroupKey()
        toOverridemodel.originKey = emission.getOriginKey()
        toOverridemodel.updateKey()
        self.overrideModelStateToModified(toOverridemodel)


    @MapperMethod(requestClass=[EmissionModel.EmissionModel, EmissionModel.EmissionModel])
    def overrideModel(self, toOverridemodel, model):
        toOverridemodel.url = model.url
        toOverridemodel.tries = model.tries
        toOverridemodel.onErrorUrl = model.onErrorUrl
        toOverridemodel.onErrorTries = model.onErrorTries
        toOverridemodel.maxTries = model.maxTries
        toOverridemodel.backOff = model.backOff
        toOverridemodel.status = model.status
        toOverridemodel.setHistory(model.history)
        self.overrideModelStateToModified(toOverridemodel)


    @MapperMethod(requestClass=[EmissionModel.EmissionModel, EnumItem])
    def overrideModelState(self, model, state):
        model.state = state


    @MapperMethod(requestClass=[[EmissionModel.EmissionModel], EnumItem])
    def overrideAllModelState(self, modelList, state):
        for model in modelList:
            self.overrideModelState(model, state)
            ConverterStatic.overrideDateData(model)


    @MapperMethod(requestClass=[EmissionModel.EmissionModel, EnumItem])
    def overrideModelStatus(self, model, status):
        model.status = status
        self.overrideModelStateToModified(model)


    @MapperMethod(requestClass=[[EmissionModel.EmissionModel], EnumItem])
    def overrideAllModelStatus(self, modelList, status):
        for model in modelList:
            self.overrideModelStatus(model, status)


    @MapperMethod(requestClass=[EmissionModel.EmissionModel])
    def overrideModelStateToModified(self, model):
        if ModelStatus.ACCEPTED == model.status:
            self.mapper.message.overrideModelState(model, ModelState.INSTANTIATED)
        else:
            self.mapper.message.overrideModelState(model, ModelState.MODIFIED)
