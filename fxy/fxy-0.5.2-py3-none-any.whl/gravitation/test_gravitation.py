from fxy.gravitation.gravity_force import F_gravity

from sympy import Eq, solve, Symbol


def test_F_gravity():

    # We have two 100 tonne balls of Tungsten at the distance of 1 meter.
    assert F_gravity.subs({
        'mass1': 100000,
        'mass2': 100000,
        'distance': 1
    }) == 0.667430000000000

    # We have two 1 g flat plates facing surface-to-surface at 10*10^-9 meter.
    assert F_gravity.subs({
        'mass1': 0.001,
        'mass2': 0.001,
        'distance': 10*10**(-9)
    }) == 0.667430000000000

    # What needs to be the distance between 1 gram objects to attract
    # each other with the force of 1 N.
    equation = Eq(
        F_gravity.subs(
            {'mass1': 0.001,
             'mass2': 0.001,
             'distance': Symbol('distance', positive=True)}), 1.0)

    res = solve(equation)[0].n()
    assert float(res.n()) == 8.169638914909276e-09

    # Don't know how to test plots, but:
    #
    # >>> from sympy import plot
    # >>> plot(F_gravity.subs({'mass1': 10, 'mass2': 10}))
    #
    # 2.01891 |
    #         |
    #         |
    #         |
    #         |
    #         |
    #         |
    #         |
    # 1.00979 | -------------------------------------------------------
    #         |
    #         |
    #         |
    #         |
    #         |
    #         |
    #         |
    #         |                           .  .
    # 6.67408 | ..........................    .........................
    #           -10                    0                          10
    #
