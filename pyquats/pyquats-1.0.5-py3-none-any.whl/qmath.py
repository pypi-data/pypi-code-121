#!/usr/bin/env python3

try:
    real_types = (int, long, float)
    range = xrange
except NameError:   # Python 3
    real_types = (int, float)

import math
import cmath
from pyquats.quats import Quat
#from pyquats.numpyquats import Quat


def exp(x):
    """Return the exponential value e**x."""
    if isinstance(x, real_types):
        return Quat(math.exp(x))
    elif isinstance(x, complex):
        # exp(a+bJ)=exp(a)*(cos(b)+sin(b)J)
        exp_real = math.exp(x.real)
        return Quat(exp_real * math.cos(x.imag), exp_real * math.sin(x.imag))
        #return Quat(1) * cmath.exp(x)
    else:   # isinstance(x, Quat)
        quat_imag = Quat(0, x.q[1], x.q[2], x.q[3])
        v = abs(quat_imag)
        #if v < 1e4:
        #    result = quat_imag * (1.0 - v*v/6.0)
        if v == 0.0:
            result = quat_imag
        else:
            result = quat_imag * (math.sin(v) / v)
        result = result + Quat(math.cos(v))
        result = result * math.exp(x.q[0])
        return result


def log(x):
    """Return the natural logarithm (base e) of x."""
    if isinstance(x, real_types):
        return Quat(math.log(x))
    elif isinstance(x, complex):
        return Quat(1) * cmath.log(x)
    else:   # isinstance(x, Quat)
        raise NotImplementedError


def sin(x):
    """Return the sine of x."""
    if isinstance(x, real_types):
        return Quat(math.sin(x))
    elif isinstance(x, complex):
        #return Quat(1) * cmath.sin(x)
        return Quat(math.sin(x.real) * math.cosh(x.imag), 
                    math.cos(x.real) * math.sinh(x.imag))
    else:   # isinstance(x, Quat)
        # sin(q)=(exp(qJ)-exp(-qJ))/(2J)
        quat = x * Quat(0, 1)
        result = exp(quat) - exp(-quat)
        result = result * Quat(0, -0.5)
        return result


def cos(x):
    """Return the cosine of x."""
    if isinstance(x, real_types):
        return Quat(math.cos(x))
    elif isinstance(x, complex):
        #return Quat(1) * cmath.cos(x)
        return Quat(math.cos(x.real) * math.cosh(x.imag), 
                   -math.sin(x.real) * math.sinh(x.imag))
    else:   # isinstance(x, Quat)
        # cos(q)=(exp(qJ)+exp(-qJ))/2
        quat = x * Quat(0, 1)
        result = exp(quat) + exp(-quat)
        result = result * Quat(0.5)
        return result


def sinh(x):
    """Return the hyperbolic sine of x."""
    if isinstance(x, real_types):
        return Quat(math.sinh(x))
    elif isinstance(x, complex):
        #return Quat(1) * cmath.sinh(x)
        return Quat(math.sinh(x.real) * math.cos(x.imag), 
                    math.cosh(x.real) * math.sin(x.imag))
    else:   # isinstance(x, Quat)
        # sin(q)=(exp(q)-exp(-q))/2
        result = exp(x) - exp(-x)
        result = result * Quat(0.5)
        return result


def cosh(x):
    """Return the hyperbolic cosine of x."""
    if isinstance(x, real_types):
        return Quat(math.cosh(x))
    elif isinstance(x, complex):
        #return Quat(1) * cmath.cosh(x)
        return Quat(math.cosh(x.real) * math.cos(x.imag), 
                    math.sinh(x.real) * math.sin(x.imag))
    else:   # isinstance(x, Quat)
        # cos(q)=(exp(q)+exp(-q))/2
        result = exp(x) + exp(-x)
        result = result * Quat(0.5)
        return result

# EOF
