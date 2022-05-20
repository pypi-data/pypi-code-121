from .core import getInput, printHelp, inputExpression, \
        inputOptionalVectorExpression

def inputBoundary(name, freestreamComments):
    # todo: we should fetch the doc from online (readthedocs or github)
    # to avoid possible inconsistency when the online doc is updated but
    # the Python client is not.  Auto fetching doc would also enable
    # adaptation of the generator to different solver versions,
    # available by calling GetMeshInfo.
    types = {'Freestream':
                'External freestream condition. Optionally, an expression ' \
                'for each of the velocity components can be specified using ' \
                'the keyword “Velocity”.',
             'NoSlipWall':
                'Sets no-slip wall condition. Optionally, ' \
                'a tangential velocity can be prescribed on the wall ' \
                'using the keyword “Velocity”.',
             'SlipWall':
                'Slip wall condition. Also used for symmetry.',
             'IsothermalWall':
                'Isothermal wall boundary condition. “Temperature” is ' \
                'specified in Kelvin. Optionally a tangential velocity can ' \
                'be presribed on the wall using the keyword “Velocity”.',
             'SubsonicOutflowPressure':
                'Subsonic outflow, enforced through static pressure ratio.',
             'SubsonicOutflowMach':
                'Static pressure outflow boundary condition set via ' \
                'a specified subsonic Mach number.',
             'SubsonicInflow':
                'Subsonic inflow (enforced via total pressure ratio and ' \
                'total temperature ratio) for nozzle or tunnel plenum.',
             'MassOutflow':
                'Specification of massflow out of the control volume.',
             'MassInflow':
                'Specification of massflow into the control volume.'
            }
    helpDoc = 'Choose a boundary condition type:\n' + \
            ('\n'.join([key + ':\n' + value for key, value in types.items()]))
    bcType = getInput('boundary condition type for ' + name,
                      helpDoc, list(types.keys()))
    return inputBcOptions(name, bcType, freestreamComments)

def inputMassFlowRate(name, helpDoc, freestreamComments):
    kgPerSecond = getInput(name, helpDoc, float)
    density = freestreamComments['densityKgPerCubicMeter']
    speedOfSound = freestreamComments['speedOfSoundMeterPerSecond']
    meshUnitLength = freestreamComments['meshUnitInMeter']
    return kgPerSecond / (density * speedOfSound * meshUnitLength**2)

def inputBcOptions(name, bcType, freestreamComments):
    # todo: we should fetch the doc from online (readthedocs or github)
    inputVelocity = lambda prompt,doc,comments: \
            inputOptionalVectorExpression(prompt,doc)
    options = {
        'Freestream': {
            'Velocity': (inputVelocity,
                'Optional: an expression for each of x,y,z component of velocity, '\
                'often used to specify an atmosphereic boundary layer.\n'\
                'Example: ["1 - exp(-z)", "0", "0"]\n' \
                'If specified, the velocity overwrites what is specified in the '\
                '"freestream" portion of the input.')
        },
        'NoSlipWall': {
            'Velocity': (inputVelocity,
                'Optional: an expression for each of x,y,z component of velocity, '\
                'often used for a moving or rotatng body.\n'\
                'Example: ["2 * cos(y)", "-2 * sin(x)", "0"] ' \
                'specifies a wall rotating around the z axis at ' \
                'an angular velocity of 2\n' \
                'If not specified, the wall velocity defaults to 0')
        },
        'SlipWall': {},
        'IsothermalWall': {
            'Temperature': (lambda prompt,doc,_: inputExpression(prompt,doc),
                'Wall temperature in Kelvins (0C is 273.15K), ' \
                'can be an expression of x, y, z, and t'),
            'Velocity': (inputVelocity,
                'Optional: an expression for each of x,y,z component of velocity, '\
                'often used for a moving or rotatng body.\n'\
                'Example: ["2 * cos(y)", "-2 * sin(x)", "0"] ' \
                'specifies a wall rotating around the z axis at ' \
                'an angular velocity of 2\n' \
                'If not specified, the wall velocity defaults to 0')
        },
        'SubsonicOutflowPressure': {
            'staticPressureRatio': (float,
                'Target ratio of boundary static pressure to ' \
                'freestream static pressure.')
        },
        'SubsonicOutflowMach': {
            'MachNumber': (float,
                'Target outflow Mach number at boundary. Must be less tan 1.')
        },
        'SubsonicInflow': {
            "totalPressureRatio" : (float,
                'Target ratio of boundary total pressure to ' \
                'freestream (static) pressure.'),
            "totalTemperatureRatio" : (float,
                'Target ratio of boundary total temperature to ' \
                'freestream temperature.'),
            "rampSteps" : (int,
                'Number of steps during which totalPressureRatio and ' \
                'totalTemperatureRatio is ramped from 1 to the target ratio.')
        },
        'MassOutflow': {
            "massFlowRate" : (inputMassFlowRate,
                'The integrated mass flow rate out of the simulation domain ' \
                'through this boundaary in SI units (kilograms per second). ' \
                'Calculate it via: Density x velocity x area.\n' \
                'Note that the value will be nondimensionalized using ' \
                'the freestream density, the freestream speed of sound, ' \
                'and the mesh unit when the input json is generated.')
        },
        'MassInflow': {
            "massFlowRate" : (inputMassFlowRate,
                'The integrated mass flow rate into the simulation domain ' \
                'through this boundaary in SI units (kilograms per second). ' \
                'Calculate it via: Density x velocity x area.\n' \
                'Note that the value will be nondimensionalized using ' \
                'the freestream density, the freestream speed of sound, ' \
                'and the mesh unit when the input json is generated.')
        }
    }

    bc = {'type': bcType}
    for key, (keyType, helpDoc) in options[bcType].items():
        if type(keyType) is type:
            bc[key] = getInput(key + ' for ' + name, helpDoc, keyType)
        else:
            value = keyType(key + ' for ' + name, helpDoc, freestreamComments)
            if value is not None:
                bc[key] = value
    return bc

def inputAllBoundaries(walls, otherBoundaries, slidingInterfaces, freestreamComments):
    printHelp()
    boundaries = {}
    for bc in walls:
        question = 'Should the default *NoSlipWall* boundary condition be applied to {}?'.format(bc)
        helpDoc = bc + ' is specified as a noSlipWall in the mesh configuration. ' \
                  'It is therefore used in wall distance calculation, ' \
                  'which affects the turbulence model.  If you answer yes ' \
                  'to the question, an adiabetic no slip wall with zero velocity ' \
                  'will be applied to this boundary. To modify this default ' \
                  'behavior, answer no to this question and specify details ' \
                  'such as wall temprature and wall velocity in the follow ' \
                  'up questions.'
        if getInput(question, helpDoc, ['y', 'n'], 'y') == 'y':
            boundaries[bc] = {"type" : "NoSlipWall"}
        else:
            boundaries[bc] = inputBoundary(bc, freestreamComments)

    slidingBoundaries = []
    for interface in slidingInterfaces:
        slidingBoundaries.extend(interface['stationaryPatches'])
        slidingBoundaries.extend(interface['rotatingPatches'])

    for bc in otherBoundaries:
        if bc in slidingBoundaries:
            boundaries[bc] = {'type': 'SlidingInterface'}
            continue
        question = 'Should the *Freestream* boundary condition be applied to {}?'.format(bc)
        helpDoc = bc + ' is *not* specified as a noSlipWall in the mesh configuration. ' \
                  'It therefore does NOT affect the wall distance calculation, ' \
                  'which is used in turbulence models. If you answer yes ' \
                  'to the question, the freestream boundary condition ' \
                  'will be applied to this boundary.  You will specify the ' \
                  'freestream Mach number, To modify this default ' \
                  'behavior, answer no to this question and specify details ' \
                  'such as wall temprature and wall velocity in the follow ' \
                  'up questions.'
        if getInput(question, helpDoc, ['y', 'n'], 'y') == 'y':
            boundaries[bc] = {"type" : "Freestream"}
        else:
            boundaries[bc] = inputBoundary(bc, freestreamComments)
    return boundaries

