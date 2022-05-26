from enum import Enum

# TODO
# class SolverStep(Enum):
#     """Step in progress within the numerical solver.
#
#     INIT : Initialization phase
#     JACOBIAN : Jacobian matrix building phase
#     ITERATION : Convergence iteration
#     """
#     INIT = 'init'
#     JACOBIAN = 'jacobian'
#     ITERATION = 'iteration'


class NonLinearMethods(Enum):
    """Enumeration of non-linear algorithm available.

    POWELL : Modified Powell method using MINPACK’s hybrd and hybrj routines
    BROYDEN_GOOD : Broyden’s first Jacobian approximation. This method is also known as “Broyden’s good method”.
    NR : Simple Newton-Raphson
    """

    POWELL = "hybr"
    BROYDEN_GOOD = "broyden1"
    NR = "cosapp"

