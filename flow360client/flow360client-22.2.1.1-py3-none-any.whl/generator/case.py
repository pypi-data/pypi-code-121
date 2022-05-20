import json
from requests.exceptions import HTTPError
from .core import getInput, printHelp, bcolors
from .meshInfo import getBoundariesAndCoordinates, displayWallBoundaries, \
                      MeshNotProcessedYetError
from .caseBoundary import inputAllBoundaries
from .caseGeometry import inputGeometry
from .caseFreestream import inputFreestream
from .caseSlidingInterfaces import inputSlidingInterfaces
from .caseTimeStepping import inputTimeStepping
from .caseNavierStokesSolver import inputNavierStokesSolverOptions
from .caseTurbulenceSolver import inputTurbulenceSolverOptions
from .caseOutput import inputVolumeSurfaceOutputOptions

def verifyJsonSection(jsonObj, sectionNames):
    for name in sectionNames:
        print('The {} section of the input is:\n'.format(name))
        print(bcolors.OKGREEN)
        print(json.dumps(jsonObj[name], indent=4, sort_keys=True))
        print(bcolors.ENDC)
    return (getInput('Is this correct?', '', ['y', 'n'], 'y') == 'y')

def inputSection(caseJson, sectionNames, inputFunc, *args):
    if type(sectionNames) is str:
        sectionNames = (sectionNames,)
    while True:
        sections = inputFunc(*args)
        if type(sections) is not tuple:
            sections = (sections,)
        assert len(sections) == len(sectionNames)
        for name, section in zip(sectionNames, sections):
            caseJson[name] = section
        if verifyJsonSection(caseJson, sectionNames):
            break

def generateCaseJson():
    """Interactive command-line generator for Flow360Case.json with explanation. Walks through following configuration sections:

        * geometry
        * freestream
        * boundaries
        * slidingInterfaces
        * timeStepping
        * navierStokesSolver
        * turbulenceModelSolver
        * volumeOutput
        * surfaceOutput

    Returns
    -------
    json (dict)
        Returns Flow360Case.json - a simulation configuration file
    """
    caseJson = {}
    try:
        printHelp()
        helpDoc = 'The mesh id is a long string that looks like\n' \
                  '123e4567-e89b-12d3-a456-426614174000\n' \
                  'It can be found either on the Flow360 web interface, '\
                  'or by calling flow360client.mesh.ListMeshes()'
        while True:
            meshId = getInput('Mesh ID', helpDoc, str)
            if meshId.strip() == '':
                continue
            try:
                walls, boundaries, slidingInterfaces = \
                        getBoundariesAndCoordinates(meshId)
                break
            except HTTPError:
                print('Error processing mesh with id ' + meshId)
        displayWallBoundaries(walls)
        helpDoc = 'The Mesh Unit is the length unit used in the mesh file. ' \
                  'It can be m (meter), cm (centimeter), mm (millimeter), ' \
                  'inch, or feet.'
        meshUnit = getInput('Mesh Unit', helpDoc,
                            ['m', 'cm', 'mm', 'inch', 'feet'])

        inputSection(caseJson, 'geometry', inputGeometry, meshUnit)
        inputSection(caseJson, 'freestream', inputFreestream, meshUnit)
        freestreamComments = caseJson['freestream']['comments']
        inputSection(caseJson, 'boundaries',
                     inputAllBoundaries, walls, boundaries, slidingInterfaces,
                     freestreamComments)
        inputSection(caseJson, 'slidingInterfaces',
                     inputSlidingInterfaces, slidingInterfaces,
                     freestreamComments)
        inputSection(caseJson, 'timeStepping',
                     inputTimeStepping, walls, freestreamComments)
        isSteady = (caseJson['timeStepping']['timeStepSize'] == 'inf')
        inputSection(caseJson, 'navierStokesSolver',
                     inputNavierStokesSolverOptions, isSteady)
        inputSection(caseJson, 'turbulenceModelSolver',
                     inputTurbulenceSolverOptions, isSteady)
        inputSection(caseJson, ('volumeOutput', 'surfaceOutput'),
                     inputVolumeSurfaceOutputOptions)
    except (KeyboardInterrupt, EOFError):
        print(bcolors.ENDC)
        print(bcolors.FAIL + 'Interrupted, returning incomplete case.')
        print(bcolors.ENDC)
    except MeshNotProcessedYetError:
        print(bcolors.ENDC)
        print(bcolors.FAIL + 'This utility works only for processed mesh.')
        print(bcolors.ENDC)
    return caseJson
