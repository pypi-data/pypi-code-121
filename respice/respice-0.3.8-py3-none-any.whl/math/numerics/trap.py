import numpy as np

from respice.math.linalg import linsys_jac


def trap(x1, h, A1, b1, A2, b2):
    r"""
    Returns the next numerical integration step for a linear differential equation system.

    For linear systems, although the trapezoidal rule is an implicit integrator, it can be solved exactly.

    .. math::

        f(t, \boldsymbol{x}) = \dot{\boldsymbol{x}} = A(t) \boldsymbol{x} + \boldsymbol{b}(t) \\
        \boldsymbol{x}_2 = \boldsymbol{x}_1 + \frac12 h (f(t_1, \boldsymbol{x}_1) + f(t_2, \boldsymbol{x}_2))

    The solution to the trapezoidal formula becomes:

    .. math::

        \left( I - \frac12 h A(t_2) \right) \boldsymbol{x}_2 =
        \boldsymbol{x}_1 + \frac12 h (A(t_1) \boldsymbol{x}_1 + \boldsymbol{b}_1 + \boldsymbol{b}_2)

    And is simply solved as a linear equation.

    :param x1:
        State :math:`x(t)` at :math:`t = t_1`.
    :param h:
        Step size.
    :param A1:
        Linear coefficient matrix :math:`A(t)` for linear system at :math:`t = t_1`.
    :param b1:
        Ordinate vector :math:`\boldsymbol{b}(t)` for linear system at :math:`t = t_1`.
    :param A2:
        Linear coefficient matrix :math:`A(t)` for linear system at :math:`t = t_2`.
    :param b2:
        Ordinate vector :math:`\boldsymbol{b}(t)` for linear system at :math:`t = t_2`.
    :return:
        The next step.
    """
    tb = x1 + 0.5 * h * (A1 @ x1 + b1 + b2)
    tA = np.identity(len(tb)) - 0.5 * h * A2
    return np.linalg.solve(tA, tb)


def trap_jac(x2, h, A2, dA2, db2):
    r"""
    Returns the Jacobian matrix of the trapezoidal rule for a linear differential equation system for any given
    variable.

    Due to the trapezoidal rule being an implicit method, the Jacobian matrix becomes a quite complex expression.
    Since the states at :math:`t = t_1` are considered to be constant (they represent an already calculated step),
    only states at :math:`t = t_2` are relevant.

    .. math::

        \left(
            I - \frac12 h A(t_2)
        \right)
        J_{\boldsymbol{x}_2}(\boldsymbol{y}) =
        \frac12 h
        \left(
            \left. \frac{\partial \boldsymbol{b}}{\partial \boldsymbol{y}} \right|_{t_2} +
            \left(
                \left. \frac{\partial A}{\partial \boldsymbol{y}} \right|_{t_2} \boldsymbol{x_2}
            \right )^{T}
        \right)

    :param x2:
        Next state :math:`x(t)` at :math:`t = t_2`.
        This is the solution of `trap(x1, h, A1, b1, A2, b2)`.
    :param h:
        Step size.
    :param A2:
        Linear coefficient matrix :math:`A(t)` for linear system at :math:`t = t_2`.
    :param dA2:
        A 3rd-order tensor containing the element-wise derivatives of each matrix entry in :math:`A(y)`
        over each :math:`y`.
    :param db2:
        The derivative matrix of :math:`b(y)`.
    :return:
        The Jacobian.
    """
    # The (0.5 * h) part can be pulled out of the linear Jacobian expression according to the formulas.
    # This improves performance.
    return 0.5 * h * linsys_jac(x2,
                                np.identity(len(x2)) - 0.5 * h * A2,
                                -dA2,
                                db2)
