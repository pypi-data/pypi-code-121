class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def printHelp():
    print(bcolors.HEADER)
    print('\nAt any time, enter "?" to get help about the current input. ' \
          'If you want to abort the process, press Ctl-D.\n')
    print(bcolors.ENDC)

def getInput(prompt, helpDoc, inputType, default=None):
    if type(inputType) is list:
        while True:
            result = getInput(prompt + ' ' + str(inputType), helpDoc, str, default)
            if result not in inputType:
                print('    Input not recognized: {} must be in {}'.format(result, inputType))
            else:
                break
        return result
    if default is not None:
        prompt = prompt + bcolors.OKBLUE + (' (default: {})'.format(default)) + bcolors.ENDC
    while True:
        val = input(prompt + ': ' + bcolors.UNDERLINE + bcolors.WARNING).strip()
        print(bcolors.ENDC)
        if val == '?':
            print()
            print(helpDoc)
            print()
            continue
        elif val == '' and default is not None:
            val = default
        try:
            return inputType(val)
        except:
            print('Cannot convert {} to type {}'.format(val, inputType))

def inputVector(prompt, helpDoc, default=[None,None,None]):
    x = getInput(prompt + ' x', helpDoc, float, default[0])
    y = getInput(prompt + ' y', helpDoc, float, default[1])
    z = getInput(prompt + ' z', helpDoc, float, default[2])
    return [x, y, z]

def inputExpression(name, helpDoc):
    # todo: verify with sympy?
    return getInput(name, helpDoc, str)

def inputOptionalVectorExpression(name, helpDoc):
    if getInput('Default?', helpDoc, ['y', 'n']) == 'y':
        return None
    x = inputExpression(name + ' (x component)', helpDoc)
    y = inputExpression(name + ' (y component)', helpDoc)
    z = inputExpression(name + ' (z component)', helpDoc)
    return [x, y, z]

def meshUnitInMeter(meshUnit):
    inMeter = {
        'm': 1,
        'cm': 0.01,
        'mm': 0.001,
        'inch': 0.0254,
        'feet': 0.3048
    }
    return inMeter[meshUnit]
