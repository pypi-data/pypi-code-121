from .core import getInput, printHelp, meshUnitInMeter, bcolors

def inputCFL(isSteady):
    CFL = {}
    helpDoc = 'The CFL number controls how agressive each iteration ' \
              'is. An iteration with smaller CFL number makes less ' \
              'progress towards convergence, but is safer from divergence. ' \
              'An iteration with larger CFL makes more progress but ' \
              'could lead to divergence when the the flow solution is ' \
              'still far from convergence.  Therefore, we recommend ' \
              'starting from a small (safe) initial CFL number of around 1, ' \
              'and ramp towards a larger final CFL number of 100 or more.'
    CFL['initial'] = getInput('Initial CFL number', helpDoc, float, 1)
    CFL['final'] = getInput('Final CFL number', helpDoc, float, 100)

    helpDoc = 'The CFL number will ramp from the initial number to ' \
              'the final number during the first part of the ' \
              'iterations.  The ramp steps control how long the ' \
              'first part is.  During the second part of the iterations, ' \
              'the CFL number will stay at the final CFL number.'
    defaultRampSteps = 2500 if isSteady else 40
    CFL['rampSteps'] = getInput('CFL ramping steps', helpDoc, int, defaultRampSteps)
    return CFL

def inputTimeStepping(walls, freestreamComments):
    timeStepping = {}
    helpDoc = 'Steady simulation attempts to converge to a ' \
              'steady-state flow solution.  Answer no for an ' \
              'unsteady simulation that solves for unsteady ' \
              'flow physics.  You will need to enter a time ' \
              'step size and number of time steps.'
    isSteady = (getInput('Is the simulation steady?', helpDoc, ['y', 'n'], 'y') == 'y')
    if isSteady:
        timeStepping['timeStepSize'] = 'inf'
        timeStepping['maxPhysicalSteps'] = 1
        prompt = 'The maximum nonlinear iterations'
        helpDoc = 'A nonlinear iteration (quasi-Newton) will be used ' \
                  'to converge the flow field.  If the maximum iteration' \
                  'number is reached without reaching tolerance, the solver ' \
                  'will output the flow solution.'
        timeStepping['maxPseudoSteps'] = getInput(prompt, helpDoc, int, 5000)
    else:
        freestream = freestreamComments['freestreamMeterPerSecond']
        print(bcolors.OKBLUE + \
              'Freestream velocity ({:.4g} m/s) '.format(freestream) + \
              'would cover your boundaries in these many seconds:')
        for name, coords in walls.items():
            box = coords.max(0) - coords.min(0)
            boxInMeter = box * freestreamComments['meshUnitInMeter']
            seconds = tuple(list(boxInMeter / freestream))
            print('{}: {:.4g} x {:.4g} x {:.4g}'.format(*(name,) + seconds))
        print(bcolors.ENDC)
        speedOfSound = freestreamComments['speedOfSoundMeterPerSecond']
        print(bcolors.OKGREEN + \
              'Freestream speed of sound ({:.4g} m/s) '.format(speedOfSound) + \
              'would cover your boundaries in these many seconds:')
        for name, coords in walls.items():
            box = coords.max(0) - coords.min(0)
            boxInMeter = box * freestreamComments['meshUnitInMeter']
            seconds = tuple(list(boxInMeter / speedOfSound))
            print('{}: {:.4g} x {:.4g} x {:.4g}'.format(*(name,) + seconds))
        print(bcolors.ENDC)
        helpDoc = 'A second-order implicit time stepping scheme will be used ' \
                  'to converge each time step.  Enter time step size here. ' \
                  'Note that the time step size will be nondimensionalized ' \
                  'using the freestream speed of sound and the mesh unit ' \
                  'when generating the input.'
        prompt = 'Time step size for unsteady simulation (seconds)'
        stepSizeSecond = getInput(prompt, helpDoc, float)
        meshUnitLength = freestreamComments['meshUnitInMeter']
        timeStepping['timeStepSize'] = stepSizeSecond / (meshUnitLength / speedOfSound)
        prompt = 'How many time steps do you want to simulate?'
        helpDoc = 'A second-order implicit time stepping scheme will be used ' \
                  'to converge each time step.  Enter number of time steps here. ' \
                  'Note that a nonlinear iteration will be used to converge ' \
                  'each time step.  You will enter the number of nonlinear ' \
                  'iterations to take next.'
        timeStepping['maxPhysicalSteps'] = getInput(prompt, helpDoc, int)

        prompt = 'The maximum nonlinear iterations use to converge each physical step'
        helpDoc = 'A nonlinear iteration (quasi-Newton) will be used ' \
                  'to converge each physical step.  When the maximum iteration' \
                  'number is reached without reaching tolerance, the solver ' \
                  'will proceed to the next time step.'
        timeStepping['maxPseudoSteps'] = getInput(prompt, helpDoc, int, 50)

        timeStepping["comments"] = {
            'timeStepSizeInSeconds': stepSizeSecond,
        }

    timeStepping['CFL'] = inputCFL(isSteady)
    return timeStepping
