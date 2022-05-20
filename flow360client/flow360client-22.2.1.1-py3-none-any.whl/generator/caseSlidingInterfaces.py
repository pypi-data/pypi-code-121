import json
import copy
from math import pi

from .core import getInput, printHelp, meshUnitInMeter, bcolors

def inputSlidingInterfaces(slidingInterfaces, freestreamComments):
    printHelp()
    interfaces = []
    for inter in slidingInterfaces:
        inter = copy.deepcopy(inter)
        inter['volumeName'] = inter['stationaryPatches'][0].split('/')[0]
        print('For the rotation interface')
        print(bcolors.OKGREEN + json.dumps(inter, indent=4, sort_keys=True))
        print(bcolors.ENDC)
        helpDoc = 'The RPM (rotations per minute) should be positive if ' \
                  'the rotation follows the right-hand rule with respect ' \
                  'to the axis of rotation (thumb pointing towards axis). ' \
                  'If the rotation follows the left-hand rule, the RPM ' \
                  'must be nevative.'
        rpm = getInput('Enter the signed RPM', helpDoc, float)
        radiansPerSec = rpm * (2*pi) / 60
        speedOfSound = freestreamComments['speedOfSoundMeterPerSecond']
        meshUnitLength = freestreamComments['meshUnitInMeter']
        inter['omega'] = radiansPerSec / (speedOfSound / meshUnitLength)
        interfaces.append(inter)
        print()
    return interfaces
