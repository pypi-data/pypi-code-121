from python_helper import log, ObjectHelper
from python_framework import Service, ServiceMethod

import Emission, EmissionModel
from constant import EmissionConstant
from enumeration.ModelState import ModelState
from enumeration.ModelStatus import ModelStatus


LOG_LEVEL = log.STATUS


@Service()
class EmissionModelService:

    @ServiceMethod(requestClass=[[Emission.Emission]])
    def createOrUpdateAll(self, emissionList):
        if ObjectHelper.isEmpty(emissionList):
            return []
        self.mapper.emission.overrideAllModelState(emissionList, ModelState.PERSISTED)
        modelList = self.mapper.emissionModel.fromRequestDtoListToModelList(emissionList)
        log.prettyPython(self.createOrUpdateAll, f'Creating or updating queued message emissions', modelList, logLevel=LOG_LEVEL)
        existingModelList = self.findAllModelByKeyIn(list({model.key for model in modelList}))
        existingModelDictionary = {
            self.helper.emissionModel.getModelKey(model): model for model in existingModelList
        }
        for model in modelList:
            if self.helper.emissionModel.getModelKey(model) in existingModelDictionary:
                self.mapper.emissionModel.overrideModel(
                    existingModelDictionary.get(self.helper.emissionModel.getModelKey(model)),
                    model
                )
            else:
                existingModelList.append(model)
        return self.persistAll(existingModelList)


    @ServiceMethod(requestClass=[[str]])
    def findAllModelByKeyIn(self, keyList):
        return self.repository.emissionModel.findAllByKeyIn(keyList)


    @ServiceMethod(requestClass=[str])
    def existsByKey(self, key):
        return self.repository.emissionModel.existsByKey(key)


    @ServiceMethod(requestClass=[[EmissionModel.EmissionModel]])
    def persistAll(self, modelList):
        self.mapper.messageModel.overrideAllModelState(modelList, ModelState.PERSISTED)
        log.prettyPython(self.createOrUpdateAll, f'Persisting queued message emissions', modelList, logLevel=LOG_LEVEL)
        return self.repository.messageModel.saveAll(modelList)
