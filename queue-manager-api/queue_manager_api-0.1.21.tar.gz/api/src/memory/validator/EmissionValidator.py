from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import EmissionDto
import Emission


@Validator()
class EmissionValidator:

    @ValidatorMethod(requestClass=[EmissionDto.EmissionRequestDto])
    def validateRequestDto(self, dto):
        self.validator.emissionModel.validateRequestDto(dto)


    @ValidatorMethod(requestClass=[EmissionDto.EmissionRequestDto])
    def validateDoesNotExists(self, dto):
        self.validator.emissionModel.validateRequestDto(dto)


    @ValidatorMethod(requestClass=[[Emission.Emission]])
    def validateAllBelongsToTheSameQueue(self, modelList):
        if not 1 == len({model.queueKey for model in modelList if ObjectHelper.isNotNone(model.queueKey)}):
            raise GlobalException(
                logEmission = f'All emissions should be from the same queue. Emissions: {modelList}',
                status = HttpStatus.INTERNAL_SERVER_ERROR
            )
