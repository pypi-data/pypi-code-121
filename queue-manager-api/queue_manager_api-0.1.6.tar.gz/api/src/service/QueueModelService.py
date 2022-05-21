from python_helper import ObjectHelper
from python_framework import Service, ServiceMethod

import QueueDto
import QueueModel
from util import AuditoryUtil


@Service()
class QueueModelService:

    @ServiceMethod()
    def findAllByOrigin(self):
        modelList = self.repository.queueModel.findAllByOriginKey(AuditoryUtil.getApiKeyIdentity(service=self))
        return self.mapper.queueModel.fromModelListToResponseDtoList(
            modelList
        )


    @ServiceMethod(requestClass=[QueueDto.QueueRequestDto])
    def createOrUpdate(self, dto):
        self.validator.queueModel.validateRequestDto(dto)
        model = self.findOptionalModelByKey(dto.key)
        if ObjectHelper.isNone(model):
            model = self.mapper.queueModel.fromRequestDtoToModel(dto, AuditoryUtil.getApiKeyIdentity(service=self))
        else:
            self.mapper.queueModel.overrideModel(model, dto)
        return self.mapper.queueModel.fromModelToResponseDto(self.persist(model))


    @ServiceMethod(requestClass=[str])
    def findModelByKey(self, key):
        self.validator.queueModel.validateExistsByKey(key)
        return self.findOptionalModelByKey(key)


    @ServiceMethod(requestClass=[str])
    def findOptionalModelByKey(self, key):
        return self.repository.queueModel.findByKey(key)


    @ServiceMethod(requestClass=[str])
    def existsByKey(self, key):
        return self.repository.queueModel.existsByKey(key)


    @ServiceMethod(requestClass=[QueueModel.QueueModel])
    def persist(self, model):
        return self.repository.queueModel.save(model)
