from .core import getInput, printHelp

def inputTurbulenceSolverOptions(isSteady):
    printHelp()
    solver = {}
    prompt = 'Type of turbulence model'
    helpDoc = 'Different turbulence models solve different equations ' \
              'to model the effect of turbulence. See\n' \
              'https://www.wikiwand.com/en/Turbulence_modeling#/Common_models\n' \
              'for common options.  We offer the Spalart Allmaras model and ' \
              'the k-Omega-SST (sometimes known just as SST) model.'
    choices = ['SpalartAllmaras', 'kOmegaSST']
    solver['modelType'] = getInput(prompt, helpDoc, choices, choices[0])

    if solver['modelType'] == 'SpalartAllmaras':
        prompt = 'Turn on the rotation-curvature correction?'
        helpDoc = 'the Spalart-Schur rotation-curvature correction accounts ' \
                  'for the effects of flow rotation (e.g., inside vortices) ' \
                  'and streamline curvature (e.g., around curved walls.)' \
                  'Note that when fluid dynamicists refer to the ' \
                  'Spalart-Allmaras model, this correct is *not* turned ' \
                  'on by default.'
        solver['rotationCorrection'] = \
                (getInput(prompt, helpDoc, ['y', 'n'], 'n') == 'y')

    if not isSteady:
        prompt = 'Turn on DDES?'
        helpDoc = 'Delayed-Detached-Eddy-Simulation (DDES) turns off ' \
                  'the turbulence model away from walls and relies on the ' \
                  'mesh and unsteady time steps to resolve the effect of ' \
                  'turbulence away from walls.  It is one of the most commonly ' \
                  'used form of hybrid RANS-LES, where RANS stands for ' \
                  'Reynolds-Averaged-Navier-Stokes and LES stands for ' \
                  'Large-Eddy-Simulation.'
        solver['DDES'] = \
                (getInput(prompt, helpDoc, ['y', 'n'], 'y') == 'y')

    prompt = 'Tolerance (absolute) of the turbulence model solver'
    if isSteady:
        helpDoc = 'The solver completes when the turbulence model equation ' \
                  'is satisfied to this tolerance (and all other equation ' \
                  'are satisfied to their respective tolerance.)'
    else:
        helpDoc = 'The solver advances to the next physical step ' \
                  'when the turbulence model equation ' \
                  'is satisfied to this tolerance (and all other equation ' \
                  'are satisfied to their respective tolerance.)'
    solver['absoluteTolerance'] = getInput(prompt, helpDoc, float, 1E-8)

    if not isSteady:
        prompt = 'Relative tolerance of the turbulence model solver'
        helpDoc = 'The solver advances to the next physical step, ' \
                  'even if the (absolute) tolerance previously prescribed ' \
                  'is not met, if the imbalance between the two sides of ' \
                  'the equation, a.k.a. the residual, reduces by a factor ' \
                  'specified by this relative tolerance.'
        solver['relativeTolerance'] = getInput(prompt, helpDoc, float, 1E-2)

    prompt = 'Number of linear iterations in each turbulence model nonlinear iteration'
    helpDoc = 'Each nonlinear (quasi-Newton) iteration requires solving ' \
              'a linear system, for which we use an iterative method. ' \
              'This parameter specifies how many linear iterations to use ' \
              'during each nonlinear iteration.'
    solver['linearIterations'] = getInput(prompt, helpDoc, int, 25)

    prompt = 'Kappa parameter in the MUSCL scheme for the turbulence model solver'
    helpDoc = 'Specify a number between -1 and 0.333.  -1 is more robust and ' \
              '0.333 is the least dissipative.'
    solver['kappaMUSCL'] = getInput(prompt, helpDoc, float, -1)

    prompt = 'Order of accuracy for the turbulence model solver'
    helpDoc = 'Specify either 1 for first-order or 2 for second-order. ' \
              'You should use second-order solver for an accurate ' \
              'flow solution.  But sometimes first-order solutions ' \
              'are useful as initial conditions for difficult cases.'
    solver['orderOfAccuracy'] = getInput(prompt, helpDoc, int, 2)
    return solver
