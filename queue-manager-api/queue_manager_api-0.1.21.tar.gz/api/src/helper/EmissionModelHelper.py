from python_helper import Constant as c
from python_helper import ObjectHelper, StringHelper
from python_framework import Helper, MapperMethod

import EmissionModel
import EmissionModelHelperStatic


@Helper()
class EmissionModelHelper:

    @MapperMethod(requestClass=[[EmissionModel.EmissionModel]])
    def getModelKeyList(self, modelList):
        return [self.getModelKey(model) for model in modelList]


    @MapperMethod(requestClass=[EmissionModel.EmissionModel])
    def getModelKey(self, model):
        return EmissionModelHelperStatic.getKey(model)
