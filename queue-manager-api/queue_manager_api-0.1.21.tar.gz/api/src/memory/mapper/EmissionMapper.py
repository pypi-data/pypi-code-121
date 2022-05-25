from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import Mapper, MapperMethod, EnumItem

import Emission
import EmissionDto
from enumeration.ModelState import ModelState
from enumeration.ModelStatus import ModelStatus


@Mapper()
class EmissionMapper:

    @MapperMethod(requestClass=[[EmissionDto.EmissionRequestDto]], responseClass=[[Emission.Emission]])
    def fromRequestDtoListToModelList(self, dtoList, modelList):
        self.overrideAllModelState(modelList, ModelState.INSTANTIATED)
        return modelList


    @MapperMethod(requestClass=[[Emission.Emission]], responseClass=[[EmissionDto.EmissionResponseDto]])
    def fromModelListToResponseDtoList(self, modelList, dtoList):
        return dtoList


    @MapperMethod(requestClass=[EmissionDto.EmissionRequestDto], responseClass=[Emission.Emission])
    def fromRequestDtoToModel(self, dto, model):
        self.overrideModelState(model, ModelState.INSTANTIATED)
        return model


    @MapperMethod(requestClass=[Emission.Emission], responseClass=[EmissionDto.EmissionResponseDto])
    def fromModelToResponseDto(self, model, dto):
        return dto


    @MapperMethod(requestClass=[Emission.Emission, EnumItem])
    def overrideModelState(self, model, state):
        model.state = state


    @MapperMethod(requestClass=[[Emission.Emission], EnumItem])
    def overrideAllModelState(self, modelList, state):
        for model in modelList:
            self.overrideModelState(model, state)


    @MapperMethod(requestClass=[Emission.Emission, EnumItem])
    def overrideModelStatus(self, model, status):
        model.status = status
        self.overrideModelStateToModified(model)


    @MapperMethod(requestClass=[[Emission.Emission], EnumItem])
    def overrideAllModelStatus(self, modelList, status):
        for model in modelList:
            self.overrideModelStatus(model, status)


    @MapperMethod(requestClass=[Emission.Emission])
    def overrideModelStateToModified(self, model):
        if ModelStatus.ACCEPTED == model.status:
            self.mapper.message.overrideModelState(model, ModelState.INSTANTIATED)
        else:
            self.mapper.message.overrideModelState(model, ModelState.MODIFIED)
