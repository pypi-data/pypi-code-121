from python_helper import ObjectHelper
from python_framework import Validator, ValidatorMethod, GlobalException, HttpStatus

import EmissionDto


@Validator()
class EmissionModelValidator:

    @ValidatorMethod(requestClass=[EmissionDto.EmissionRequestDto])
    def validateRequestDto(self, dto):
        if ObjectHelper.isNone(dto) or ObjectHelper.isNone(dto.key):
            raise GlobalException(
                message = f'Emission key cannot be None',
                logMessage = f'Subscription: {dto}',
                status = HttpStatus.BAD_REQUEST
            )


    @ValidatorMethod(requestClass=[EmissionDto.EmissionRequestDto])
    def validateDoesNotExists(self, dto):
        self.validateRequestDto(dto)
        self.validateDoesNotExistsByKey(dto.key)


    @ValidatorMethod(requestClass=[str])
    def validateDoesNotExistsByKey(self, key):
        if ObjectHelper.isNone(key) or self.service.emissionModel.existsByKey(key):
            raise GlobalException(
                message = 'Emission aleady exists',
                logMessage = f'Emission {key} aleady exists',
                status = HttpStatus.BAD_REQUEST
            )
