forceKeysMap = dict({
    "CL":"CL", "CD":"CD",
    "Cfx":"CFx", "Cfy":"CFy", "Cfz":"CFz",
    "Cmx":"CMx", "Cmy":"CMy", "Cmz":"CMz",
    "CL_p":"CLPressure", "CD_p":"CDPressure",
    "Cfx_p":"CFxPressure", "Cfy_p":"CFyPressure", "Cfz_p":"CFzPressure",
    "Cmx_p":"CMxPressure", "Cmy_p":"CMyPressure", "Cmz_p":"CMzPressure",
    "CL_v":"CLSkinFriction", "CD_v":"CDSkinFriction",
    "Cfx_v":"CFxSkinFriction", "Cfy_v":"CFySkinFriction", "Cfz_v":"CFzSkinFriction",
    "Cmx_v":"CMxSkinFriction", "Cmy_v":"CMySkinFriction", "Cmz_v":"CMzSkinFriction"
})

def updateTotalForceHeaderToV2(caseId, inputDict):
    outputDict = dict()
    outputDict['steps'] = inputDict['step']
    for key in inputDict:
        if key == "step":
            continue
        underScoreIndex = key.find('_')
        forceKey = key[underScoreIndex+1:]
        assert(forceKey in forceKeysMap)
        forceKeyNew = forceKeysMap[forceKey]
        outputDict[forceKeyNew] = inputDict[key]
    return outputDict

def validateSurfaceNames(caseBnds, surfNames):
    if surfNames == None:
        return
    allSurfNames = []
    for key, value in caseBnds.items():
        if 'name' in value:
            allSurfNames.append(value['name'])
        else:
            allSurfNames.append(key)
    for inputName in surfNames:
        if inputName not in allSurfNames:
            raise ValueError(f"input surface name {inputName} doesn't exist.")

def getSurfIdToSurfName(caseBnds, orderedPatchNames):
    surfIdToName = dict()
    for surfId, patchName in enumerate(orderedPatchNames):
        assert(patchName in caseBnds)
        if 'name' in caseBnds[patchName]:
            surfIdToName[surfId] = caseBnds[patchName]['name']
        else:
            surfIdToName[surfId] = patchName
    return surfIdToName

def updateSurfForceHeaderToV2(caseBnds, orderedPatchNames, inputDict):
    surfIdToName = getSurfIdToSurfName(caseBnds, orderedPatchNames)
    outputDict = dict()
    outputDict['steps'] = inputDict['step']
    for key in inputDict:
        if key == "step":
            continue
        underScoreIndex = key.find('_')
        surfId0Based = int(key[:underScoreIndex])
        surfName = surfIdToName[surfId0Based]

        forceKey = key[underScoreIndex+1:]
        assert(forceKey in forceKeysMap)
        forceKeyNew = forceKeysMap[forceKey]

        keyNew = surfName + "_" + forceKeyNew
        outputDict[keyNew] = inputDict[key]
    return outputDict

