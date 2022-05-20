from math import sqrt, pow
from .core import getInput, printHelp, meshUnitInMeter

def inputFreestream(meshUnit):
    printHelp()
    helpDoc = 'What is the freestream density in kilograms per cubic meter (kg/m^3)?\n' \
              'See\nhttps://www.wikiwand.com/en/U.S._Standard_Atmosphere\n' \
              'for the US standard atmosphere.  For standard sea level ' \
              'condition, enter 1.225.  For the International standard atmosphere, see\n' \
              'https://www.wikiwand.com/en/International_Standard_Atmosphere#/Description\n' \
              'for standard values at different altitude.  Be sure to use ' \
              'the value with a unit of kg/m^3.'
    density = getInput('Freestream density in kg/m^3', helpDoc, float, 1.225)
    helpDoc = 'What is the freestream temperature in Kelvin (K)?\n' \
              'See\nhttps://www.wikiwand.com/en/U.S._Standard_Atmosphere\n' \
              'for the US standard atmosphere.  For standard sea level ' \
              'condition, enter 288.15.  For the International standard atmosphere, see\n' \
              'https://www.wikiwand.com/en/International_Standard_Atmosphere#/Description\n' \
              'for standard values at different altitude.  Be sure to use ' \
              'the value with a unit of Kelvin (K).'
    temperature = getInput('Freestream temperature in Kelvin', helpDoc, float, 288.15)

    R = 287.0529
    pressure = R * density * temperature
    viscosity = 1.458E-6 * pow(temperature, 1.5) / (temperature + 110.4)
    speedOfSound = sqrt(1.4 * R * temperature)
    print('\nThe freestream pressure is calculated to be {} [Pa]'.format(pressure))
    print('The freestream dynamic viscosity is calculated to be {} [kg/(m s)]'.format(viscosity))
    print('The freestream speed of sound is calculated to be {} [m/s]\n'.format(speedOfSound))

    helpDoc = 'What is the freestream velocity in meters per second?. Note that ' \
              'the Mach number of the freestream will be this velocity divided ' \
              'by the freestream speed of sound calculated above.'
    speed = getInput('Freestream velocity in m/s', helpDoc, float)

    Mach = speed / speedOfSound
    muRef = viscosity / (density * speedOfSound * meshUnitInMeter(meshUnit))

    if Mach > 0:
        prompt = 'Do you want to use the freestream velocity as the ' \
                 'reference velocity for calculating aerodynamic coefficients?\n'
        helpDoc = 'The reference velocity is used in calculating the ' \
                  'lift coefficient and drag coefficients:\n' \
                  'CL = Lift / (0.5 * (freestream density) * (reference velocity)^2)\n' \
                  'CD = drag / (0.5 * (freestream density) * (reference velocity)^2)\n' \
                  'This is done both for the entire vehicle ' \
                  '(all viscous wall boundaries) and for each separate boundary.\n' \
                  'The reference velocity is also used in calculating ' \
                  'the force coefficients and moment coefficients:\n' \
                  'CFx = (X-force) / (0.5 * (freestream density) * (reference velocity)^2)\n' \
                  'CFy = (Y-force) / (0.5 * (freestream density) * (reference velocity)^2)\n' \
                  'CFz = (Z-force) / (0.5 * (freestream density) * (reference velocity)^2)\n' \
                  'CMx = (X-moment) / (0.5 * (freestream density) * (reference velocity)^2 * (X-moment-length)\n' \
                  'CMy = (Y-moment) / (0.5 * (freestream density) * (reference velocity)^2 * (Y-moment-length)\n' \
                  'CMz = (Z-moment) / (0.5 * (freestream density) * (reference velocity)^2 * (Z-moment-length)\n' \
                  'where the moment lengths are defined in the ' \
                  'Geometry section of the input.\n' \
                  'In addition, the reference velocity is used in ' \
                  'calculating the pressure coefficient and the ' \
                  'skin friction coefficient.'
        if getInput(prompt, helpDoc, ['y', 'n'], 'y') == 'y':
            velRef = None
        else:
            velRef = getInput('Reference velocity in m/s', helpDoc, float)
    else:
        velRef = getInput('Reference velocity in m/s', helpDoc, float)

    helpDoc = 'The X,Y, and Z components ' \
              'of the freestream velocity is initialized according to the ' \
              'angle of attack (alpha) and the side slip angle (beta) ' \
              'according to the following equatio:\n' \
              '(X velocity) =  (Freestream velocity) * cosd(beta) * cosd(alpha)\n' \
              '(Y velocity) = -(Freestream velocity) * sind(beta)\n' \
              '(Z velocity) =  (Freestream velocity) * cosd(beta) * sind(alpha)\n'
    helpDocA = 'The angle of attack in degrees.\n' + helpDoc
    alpha = getInput('Angle of attack alpha', helpDocA, float, 0)
    helpDocB = 'The side slip angle in degrees.\n' + helpDoc
    beta = getInput('Side slip angle beta', helpDocB, float, 0)

    freestream = {
        'muRef': muRef,
        'Mach': Mach,
        'Temperature': temperature,
        'alphaAngle': alpha,
        'betaAngle': beta
    }
    if velRef is not None:
        freestream['MachRef'] = velRef / speedOfSound

    freestream["comments"] = {
        'densityKgPerCubicMeter': density,
        'speedOfSoundMeterPerSecond': speedOfSound,
        'freestreamMeterPerSecond': speed,
        'meshUnitInMeter': meshUnitInMeter(meshUnit)
    }
    return freestream
