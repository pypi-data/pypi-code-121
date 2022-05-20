try:
    import h5py
    _H5PY_AVAILABLE = True
except ImportError:
    _H5PY_AVAILABLE = False

import warnings
import numpy as np
from .version import Flow360Version

def getSubNodeNames(node):
    return [subName for subName in node 
            if subName != ' data']

def convertIntDatasetToStr(dataset):
    dataRaw = np.empty(dataset.shape, dataset.dtype)
    dataset.read_direct(dataRaw)
    dataStr = "".join([chr(i) for i in dataset])
    return dataStr

def checkValidZone(zone):
    if 'label' not in zone.attrs:
        return False
    if zone.attrs['label'].decode() != "Zone_t":
        return False
    zoneType = zone['ZoneType'][' data']
    typeInStr = convertIntDatasetToStr(zoneType)
    if typeInStr in ['Structured', 'Unstructured']:
        return True
    return False

def getElementsTypeSectionNames(zone):
    sectionsRaw = getSubNodeNames(zone)
    sectionsInElementsType = list()
    for sec in sectionsRaw:
        if 'label' not in zone[sec].attrs:
            continue
        label = zone[sec].attrs['label'].decode()
        if label == 'Elements_t':
            sectionsInElementsType.append(sec)
    return sectionsInElementsType

def Is2DElementSection(section):
    elementTypeTag = int(section[' data'][0])

    if elementTypeTag in [5, 7]:
        return True
    elif elementTypeTag in [10,12,14,17]:
        return False
    elif elementTypeTag == 20:
        assert('ElementConnectivity' in section)
        connDataSet = section['ElementConnectivity'][' data']
        firstElementTypeTag = int(connDataSet[0])
        if firstElementTypeTag in [5,7]:
            return True
        elif firstElementTypeTag in [10,12,14,17]:
            return False
        else:
            raise RuntimeError('Some elements in CGNS mesh are not supported. The element type = {:d}'.format(firstElementTypeTag))
    else:
        raise RuntimeError('Some elements in CGNS mesh are not supported. The element type = {:d}'.format(elementTypeTag))

def getBoundaryNamesFromZoneNoSlash(zone):
    boundaryNamesNoSlash = list()
    subNodeNames = getSubNodeNames(zone)
    for subName in subNodeNames:
        subNode = zone[subName]
        if 'label' not in subNode.attrs:
            continue
        label = subNode.attrs['label'].decode()
        if label == 'ZoneBC_t':
            for bcName in subNode:
                bcNode = subNode[bcName]
                if 'label' not in bcNode.attrs:
                    continue
                label = bcNode.attrs['label'].decode()
                if label == 'BC_t':
                    boundaryNamesNoSlash.append(bcName)
    return boundaryNamesNoSlash

def implGetBoundaryCompoundNamesFromCGNS_v1(meshFile):
    with h5py.File(meshFile, "r") as fh:
        base = fh['Base']
        zoneNamesRaw = getSubNodeNames(base)
        zoneNames = [zone for zone in zoneNamesRaw 
                     if checkValidZone(base[zone])]
        boundaryCompleteNames = list()
        for zoneName in zoneNames:
            zone = base[zoneName]
            elementSectionNames = getElementsTypeSectionNames(zone)
            for secName in elementSectionNames:
                section = zone[secName]
                if Is2DElementSection(section):
                    boundaryCompleteNames.append(zoneName+'/'+secName)
        return boundaryCompleteNames

def implGetBoundaryCompoundNamesFromCGNS_v2(meshFile):
    with h5py.File(meshFile, "r") as fh:
        base = fh['Base']
        zoneNamesRaw = getSubNodeNames(base)
        zoneNames = [zone for zone in zoneNamesRaw 
                     if checkValidZone(base[zone])]
        boundaryCompleteNames = list()
        for zoneName in zoneNames:
            zone = base[zoneName]
            bndNames = getBoundaryNamesFromZoneNoSlash(zone)
            for bndName in bndNames:
                boundaryCompleteNames.append(zoneName+'/'+bndName)
        return boundaryCompleteNames

def getBoundaryCompoundNamesFromCGNS(meshFile, solverVersion):
    if solverVersion == None:
        return implGetBoundaryCompoundNamesFromCGNS_v1(meshFile)
    elif Flow360Version(solverVersion) < Flow360Version('release-22.2.1.0'):
        return implGetBoundaryCompoundNamesFromCGNS_v1(meshFile)
    else:
        return implGetBoundaryCompoundNamesFromCGNS_v2(meshFile)

def getNotFoundBoundaries(inputBndNames, availableBndNames):
    return [bnd for bnd in inputBndNames if bnd not in availableBndNames]

def getWallsInCGNSMesh(meshFile):
    walls = list()
    with h5py.File(meshFile, "r") as fh:
        base = fh['Base']
        zoneNamesRaw = getSubNodeNames(base)
        for zoneName in zoneNamesRaw:
            zone = base[zoneName]
            if 'FamBC_TypeName' in zone:
                typeNameStr = convertIntDatasetToStr(zone['FamBC_TypeName'][' data'])
                if typeNameStr == 'Wall' or 'Wall Viscous' in typeNameStr:
                    walls.append(zoneName)
    return walls

def compareWallsInMesh(meshFile, wallsInput, title=''):
    wallsInMesh = getWallsInCGNSMesh(meshFile)
    for wallInMesh in wallsInMesh:
        if wallInMesh not in " ".join(wallsInput):
            print('Notice: {} is tagged as wall in mesh file, but not in {} input json'.format(wallInMesh, title))

def validateMeshAndMeshJson(meshName, meshJson, solverVersion=None):
    if not meshName.endswith('.cgns'):
        print('Validation of mesh file with json file during submission is only available for .cgns mesh.')
        return True
    if not _H5PY_AVAILABLE:
        warnings.warn('Could not check consistency between mesh file and Flow360Mesh.json file. h5py module not found. This is optional functionality')
    else:
        boundaryCompoundNames = getBoundaryCompoundNamesFromCGNS(meshName, solverVersion)
        
        bndsNotInMesh = list()
        if 'boundaries' in meshJson and 'noSlipWalls' in meshJson['boundaries']:
            bndsNotInMesh += getNotFoundBoundaries(meshJson['boundaries']['noSlipWalls'], boundaryCompoundNames)
            # give suggestions on walls from mesh, non-blocking
            compareWallsInMesh(meshName, meshJson['boundaries']['noSlipWalls'], 'mesh')
            
        if 'slidingInterfaces' in meshJson:
            for slidingInterface in meshJson['slidingInterfaces']:
                bndsNotInMesh += getNotFoundBoundaries(slidingInterface['stationaryPatches'], boundaryCompoundNames)
                bndsNotInMesh += getNotFoundBoundaries(slidingInterface['rotatingPatches'], boundaryCompoundNames)
        if len(bndsNotInMesh) > 0:
            raise ValueError('The following input boundary names from mesh json are not found in mesh: {}. All available boundary names: {}'.format(", ".join(bndsNotInMesh), ", ".join(boundaryCompoundNames)))
    return True

def validateMeshAndCaseJson(meshName, caseJson, solverVersion=None):
    if not meshName.endswith('.cgns'):
        warnings.warn('The current capability only works for .cgns mesh.')
        return True
    if not _H5PY_AVAILABLE:
        warnings.warn('Could not check consistency between mesh file and Flow360.json file. h5py module not found. This is optional functionality')
    else:
        boundaryCompoundNames = getBoundaryCompoundNamesFromCGNS(meshName, solverVersion)
        assert('boundaries' in caseJson)
        caseBoundaries = caseJson['boundaries']
        # give suggestions on walls from mesh, non-blocking
        noSlipWalls = [bname for bname in caseBoundaries if caseBoundaries[bname]['type']=='NoSlipWall']
        compareWallsInMesh(meshName, noSlipWalls, 'case')
 
        bndsNotInMesh = list()
        bndsNotInMesh += getNotFoundBoundaries(list(caseBoundaries.keys()), boundaryCompoundNames)

        bndsNotInCaseJson = list()
        bndsNotInCaseJson += getNotFoundBoundaries(boundaryCompoundNames, list(caseBoundaries.keys()))

        if 'slidingInterfaces' in caseJson:
            for slidingInterface in caseJson['slidingInterfaces']:
                bndsNotInMesh += getNotFoundBoundaries(slidingInterface['stationaryPatches'], boundaryCompoundNames)
                bndsNotInMesh += getNotFoundBoundaries(slidingInterface['rotatingPatches'], boundaryCompoundNames)

        errorMsg = ""
        if len(bndsNotInMesh) > 0:
            errorMsg += "The following input boundary names from case json are not found in mesh: {}".format(", ".join(bndsNotInMesh))
        if len(bndsNotInCaseJson) > 0:
            errorMsg += "\nThe following boundary names from mesh are missing in case json: {}".format(", ".join(bndsNotInCaseJson))

        if len(bndsNotInMesh)>0 or len(bndsNotInCaseJson)>0:
            raise ValueError(errorMsg)
    return True



