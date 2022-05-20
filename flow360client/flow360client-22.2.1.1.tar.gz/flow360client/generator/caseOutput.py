from .core import printHelp, getInput

def inputOutputOption(output, name, helpDoc, default):
    default = 'y' if default else 'n'
    output[name] = (getInput(name + '?', helpDoc, ['y', 'n'], default) == 'y')

def inputVolumeSurfaceOutputOptions():
    printHelp()
    volumeOutput, surfaceOutput = {}, {}
    outputFormat = getInput('Output format', '', ['tecplot', 'paraview'],
                            'tecplot')
    volumeOutput['outputFormat'] = outputFormat
    surfaceOutput['outputFormat'] = outputFormat
    printHelp()
    helpDoc = ''
    print('For volume output:')
    inputOutputOption(volumeOutput, 'primitiveVars', helpDoc, False)
    inputOutputOption(volumeOutput, 'vorticity', helpDoc, False)
    inputOutputOption(volumeOutput, 'Cp', helpDoc, True)
    inputOutputOption(volumeOutput, 'Mach', helpDoc, True)
    inputOutputOption(volumeOutput, 'qcriterion', helpDoc, True)
    printHelp()
    print('For surface output:')
    inputOutputOption(surfaceOutput, 'Cp', helpDoc, True)
    inputOutputOption(surfaceOutput, 'Cf', helpDoc, False)
    inputOutputOption(surfaceOutput, 'CfVec', helpDoc, True)
    return volumeOutput, surfaceOutput
