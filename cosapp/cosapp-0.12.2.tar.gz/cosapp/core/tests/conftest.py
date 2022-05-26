import pytest
import numpy
import scipy

from cosapp.systems import System
from cosapp.ports import Port
from cosapp.core.numerics.residues import Residue

# <codecell>

class BogusPort(Port):
    def setup(self):
        self.add_variable('q')

class FooBar(System):
    def setup(self):
        self.add_outward('z')
        self.add_input(BogusPort, 'in_', variables={'q': 5.})

class Bogus(System):
    def setup(self):
        self.add_property('g', 9.80665)
        self.add_property('NA', 6.02214076e23)
        self.add_inward('a', 2.0)
        self.add_inward('x', numpy.r_[0.1, -0.2, -3.14])
        self.add_inward('y', numpy.ones(3))
        self.add_outward('b', 0.5)

        self.add_child(FooBar('sub'))
        self.add_child(FooBar('B52'))
        self.add_output(BogusPort, 'out', variables={'q': 0.5})

@pytest.fixture(scope="function")
def eval_context():
    """Returns a bogus system used only to provide a valid context"""
    return Bogus('bogus')

# <codecell>

@pytest.fixture(scope="function")
def ufunc_test_data():
    ufunc_data = {
        'arange': {'str': 'arange(0, 10, 2)', 'check_val': numpy.arange(0, 10, 2)},
        'array': {'str': 'array(x)',
                    'check_func': numpy.array,
                    'args': {'x': {'value': [-1., 0., 1.]}}},
        'asarray': {'str': 'asarray(x)',
                    'check_func': numpy.asarray,
                    'args': {'x': {'value': [-1., 0., 1.]}}},
        'concatenate': {
            'str': 'concatenate(x)',
            'check_func': numpy.concatenate,
            'args': {
                'x': {'value': (numpy.random.random(6), numpy.random.random(4))},
                },
            },
        'dot': {'str': 'dot(x, y)',
                'check_func': numpy.dot,
                'args': {
                    'x': {'value': numpy.random.random(6)},
                    'y': {'value': numpy.random.random(6)}}},
        'evaluate_residue': {'str': 'evaluate_residue(x, y)',
                    'check_func': Residue.evaluate_residue,
                    'args': {
                        'x': {'value': 25.},
                        'y': {'value': -12.}}},
        'fmax': {'str': 'fmax(x, y)',
                    'check_func': numpy.fmax,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'fmin': {'str': 'fmin(x, y)',
                    'check_func': numpy.fmin,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'inner': {'str': 'inner(x, y)',
                    'check_func': numpy.inner,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'isinf': {'str': 'isinf(x)',
                    'check_func': numpy.isinf,
                    'args': {
                        'x': {'value': [0, numpy.inf, 5.0]}}},
        'isnan': {'str': 'isnan(x)',
                    'check_func': numpy.isnan,
                    'args': {
                        'x': {'value': [0, numpy.nan, numpy.nan]}}},
        'kron': {'str': 'kron(x, y)',
                    'check_func': numpy.kron,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'linspace': {'str': 'linspace(0, 10, 50)',
                'check_val': numpy.linspace(0, 10, 50),
            },
        'matmul': {'str': 'matmul(x, y)',
                    'check_func': numpy.matmul,
                    'args': {
                        'x': {'value': numpy.random.random((3, 3))},
                        'y': {'value': numpy.random.random((3, 1))}}},
        'maximum': {'str': 'maximum(x, y)',
                    'check_func': numpy.maximum,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'minimum': {'str': 'minimum(x, y)',
                    'check_func': numpy.minimum,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'ones': {'str': 'ones(21)', 'check_val': numpy.ones(21)},
        'full': {
                'str': 'full((3, 7), 3.14159)',
                'check_val': numpy.full((3, 7), 3.14159),
            },
        'full_like': {'str': 'full_like(x, 3.14159)',
                    'check_val': numpy.full((3, 7), 3.14159),
                    'args': {'x': {'value': numpy.random.random((3, 7))}}},
        'cross': {'str': 'cross(x, y)',
                    'check_func': numpy.cross,
                    'args': {
                        'x': {'value': numpy.random.random(3)},
                        'y': {'value': numpy.random.random(3)}}},
        'outer': {'str': 'outer(x, y)',
                    'check_func': numpy.outer,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6)}}},
        'power': {'str': 'power(x, y)',
                    'check_func': numpy.power,
                    'args': {
                        'x': {'value': numpy.random.random(6)},
                        'y': {'value': numpy.random.random(6) + 1.0}}},
        'residue_norm': {'str': 'residue_norm(x, y)',
                    'check_func': Residue.residue_norm,
                    'args': {
                        'x': {'value': 25.},
                        'y': {'value': -12.}}},
        'round': {'str': 'round(x, y)',
            'check_func': numpy.round,
            'args': {
                'x': {'value': numpy.random.random(6)},
                'y': {'value': 4},
                },
            },
        'tensordot': {'str': 'tensordot(x, y)',
                        'check_func': numpy.tensordot,
                        'args': {
                            'x': {'value': numpy.random.random((6,6))},
                            'y': {'value': numpy.random.random((6,6))}}},
        'zeros': {'str': 'zeros(21)', 'check_val': numpy.zeros(21)}
    }

    # Add base types
    for dtype in (
        numpy.int8, numpy.int16, numpy.int32, numpy.int64,
        numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64,
        numpy.float32, numpy.float64,
        numpy.complex64, numpy.complex128,
    ):
        name = dtype.__name__
        ufunc_data[name] = {
            'str': f'zeros(5, dtype={name})',
            'check_val': numpy.zeros(5, dtype=dtype)
        }

    def add_func(func, x=numpy.random.random(10), alias=None):
        name = alias or func.__name__
        ufunc_data[name] = {
            'str': f'{name}(x)',
            'check_func': func,
            'args': {'x': {'value': x}},
        }

    # Add simple ufuncs
    for func in (
        numpy.cos, numpy.sin, numpy.tan, numpy.arctan,
        numpy.cosh, numpy.sinh, numpy.tanh, numpy.arctanh,
        numpy.exp, numpy.expm1,
        numpy.log, numpy.log10, numpy.log1p,
        numpy.sqrt, numpy.cbrt,
        numpy.prod, numpy.sum,
        numpy.linalg.norm,
        scipy.special.factorial,
        scipy.special.erf, scipy.special.erfc,
    ):
        add_func(func, numpy.random.random(10))

    for func in (numpy.arccos, numpy.arcsin):
        add_func(func, numpy.random.random(6) - 0.5)

    for func in (numpy.arccosh, numpy.arcsinh):
        add_func(func, numpy.random.random(6) + 1.1)

    # Add common short names
    add_func(numpy.abs, alias='abs')
    add_func(numpy.arctan, alias='atan')
    add_func(numpy.arcsin, alias='asin', x=numpy.random.random(6) - 0.5)
    add_func(numpy.arccos, alias='acos', x=numpy.random.random(6) - 0.5)
    add_func(numpy.arctanh, alias='atanh')
    add_func(numpy.arcsinh, alias='asinh')
    add_func(numpy.arccosh, alias='acosh', x=numpy.random.random(6) + 1.1)

    # Add constants
    for name in ('e', 'pi', 'inf'):
        ufunc_data[name] = {'str': name, 'check_val': getattr(numpy, name)}

    return ufunc_data
