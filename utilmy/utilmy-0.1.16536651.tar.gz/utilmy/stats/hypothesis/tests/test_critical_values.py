
from utilmy.stats.hypothesis import critical as c
import numpy as np
from numpy.testing import *



dof, alpha = 10, 0.05

def test_critical_values():
    """ TestWCritical:test_critical_values
    Args:
    Returns:

    """
    """ TestUCritical:test_critical_values
    Args:
    Returns:
       
    """
    """ TestRCritical:test_critical_values
    Args:
    Returns:
       
    """
    """ TestChiSquareCritical:test_critical_values
    Args:
    Returns:
       
    """
    critical_value = c.chi_square_critical_value(alpha, dof)
    critical_value2 = c.chi_square_critical_value(str(alpha), str(dof))
    critical_value3 = c.chi_square_critical_value(str(alpha), float(dof))

    assert critical_value == 18.307
    assert critical_value2 == 18.307
    assert critical_value3 == 18.307

def test_exceptions():
    """ TestWCritical:test_exceptions
    Args:
    Returns:

    """
    """ TestUCritical:test_exceptions
    Args:
    Returns:
       
    """
    """ TestRCritical:test_exceptions
    Args:
    Returns:
       
    """
    """ TestChiSquareCritical:test_exceptions
    Args:
    Returns:
       
    """
    with pytest.raises(ValueError):
        c.chi_square_critical_value(31, 0.05)
    with pytest.raises(ValueError):
        c.chi_square_critical_value(5, 1)
    with pytest.raises(ValueError):
        c.chi_square_critical_value(0.05, 31)



alpha = 0.05
n, m = 10, 11

def test_critical_values():
    critical_value = c.u_critical_value(n, m, alpha)
    critical_value2 = c.u_critical_value(str(n), str(m), str(alpha))

    assert critical_value == 31
    assert critical_value2 == 31

def test_exceptions():
    with pytest.raises(ValueError):
        c.u_critical_value(31, 10, 0.05)
    with pytest.raises(ValueError):
        c.u_critical_value(10, 31, 0.05)
    with pytest.raises(ValueError):
        c.u_critical_value(10, 10, 0.50)



n, alpha, alternative = 15, 0.05, 'two-tail'

def test_critical_values():
    crit_val = c.w_critical_value(n, alpha, alternative)
    crit_val2 = c.w_critical_value(str(n), str(alpha), alternative)

    assert crit_val == 25
    assert crit_val2 == 25

def test_exceptions():
    with pytest.raises(ValueError):
        c.w_critical_value(31, 0.05, 'two-tail')
    with pytest.raises(ValueError):
        c.w_critical_value(20, 0.02, 'two-tail')
    with pytest.raises(ValueError):
        c.w_critical_value(25, 0.05, 'three-tail')



n1, n2, n3, n4 = 4, 20, 7, 15

def test_critical_values():
    r_crit1, r_rcrit2 = c.r_critical_value(n1, n2)
    r_crit3, r_rcrit4 = c.r_critical_value(n3, n4)

    assert_allclose([r_crit1, r_rcrit2], [4, np.nan])
    assert_allclose([r_crit3, r_rcrit4], [6, 15])

def test_exceptions():
    with pytest.raises(ValueError):
        c.r_critical_value(10, 25)
    with pytest.raises(ValueError):
        c.r_critical_value(25, 15)
