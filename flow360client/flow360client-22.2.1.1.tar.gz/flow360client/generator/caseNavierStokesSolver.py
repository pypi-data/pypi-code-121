from .core import getInput, printHelp

def inputNavierStokesSolverOptions(isSteady):
    printHelp()
    solver = {}
    prompt = 'Tolerance (absolute) of the Navier-Stokes solver'
    if isSteady:
        helpDoc = 'The solver completes when the Navier-Stokes equation ' \
                  'is satisfied to this tolerance (and all other equation ' \
                  'are satisfied to their respective tolerance.)'
    else:
        helpDoc = 'The solver advances to the next physical step ' \
                  'when the Navier-Stokes equation ' \
                  'is satisfied to this tolerance (and all other equation ' \
                  'are satisfied to their respective tolerance.)'
    solver['absoluteTolerance'] = getInput(prompt, helpDoc, float, 1E-9)
    if not isSteady:
        prompt = 'Relative tolerance of the Navier-Stokes solver'
        helpDoc = 'The solver advances to the next physical step, ' \
                  'even if the (absolute) tolerance previously prescribed ' \
                  'is not met, if the imbalance between the two sides of ' \
                  'the equation, a.k.a. the residual, reduces by a factor ' \
                  'specified by this relative tolerance.'
        solver['relativeTolerance'] = getInput(prompt, helpDoc, float, 1E-2)
    prompt = 'Number of linear iterations in each Navier-Stokes nonlinear iteration'
    helpDoc = 'Each nonlinear (quasi-Newton) iteration requires solving ' \
              'a linear system, for which we use an iterative method. ' \
              'This parameter specifies how many linear iterations to use ' \
              'during each nonlinear iteration.'
    solver['linearIterations'] = getInput(prompt, helpDoc, int, 35)
    prompt = 'Kappa parameter in the MUSCL scheme for the Navier-Stokes solver'
    helpDoc = 'Specify a number between -1 and 0.333.  -1 is more robust and ' \
              '0.333 is the least dissipative.'
    solver['kappaMUSCL'] = getInput(prompt, helpDoc, float, -1)
    prompt = 'Order of accuracy for the Navier-Stokes solver'
    helpDoc = 'Specify either 1 for first-order or 2 for second-order. ' \
              'You should use second-order solver for an accurate ' \
              'flow solution.  But sometimes first-order solutions ' \
              'are useful as initial conditions for difficult cases.'
    solver['orderOfAccuracy'] = getInput(prompt, helpDoc, int, 2)
    return solver
