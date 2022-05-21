from python_helper import ObjectHelper


def getManyToOneData(model, modelId, refferenceModel):
    return model, modelId if ObjectHelper.isNone(model) or not isinstance(model, refferenceModel.__class__) else model.id


def getOneToManyData(modelList):
    return [] if ObjectHelper.isEmpty(modelList) else modelList
