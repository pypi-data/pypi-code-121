import pytest

import numpy as np

from cosapp.core.eval_str import AssignString
from cosapp.ports.enum import PortType


@pytest.mark.parametrize("lhs", [
    "x[2]",
    "x[-1]",
    "inwards.x[-1]",
    ])
def test_AssignString__init__(eval_context, lhs):
    context = eval_context  # for convenience
    assert context is eval_context
    context.x[2] = 0.1
    assert context.x[2] == 0.1

    rhs = 'a + b'
    s = AssignString(lhs, rhs, context)
    assert s.lhs == lhs
    assert s.rhs == rhs
    assert str(s) == f"{lhs} = {rhs}"
    assert s.eval_context is context
    assert context.x[2] == 0.1
    assert s.contextual_lhs == f"bogus.{lhs}"
    
    context.a = 0.9
    context.b = 1.7
    value, changed = s.exec()
    assert value == pytest.approx(2.6, rel=1e-14)
    assert context.x[2] == value
    assert changed
    
    context.a = 0.1
    context.b = 0.3
    value, changed = s.exec()
    assert changed
    assert value == pytest.approx(0.4, rel=1e-14)
    assert context.x[2] == value


@pytest.mark.parametrize("lhs, rhs, exception", [
    (0, 0, ValueError),
    ("0", 0, ValueError),
    ("0", "0", ValueError),
    ("0", "a + b", ValueError),
    ("a + b", "0", SyntaxError),
    ("-", "0", SyntaxError),
    ("x[", "0", SyntaxError),
    ("a", "b +", SyntaxError),
    ("a[:]", "b", TypeError),
    ("_a", "b", NameError),
    ("a", "-", SyntaxError),
    ("a + b", "0", SyntaxError),
    ("a + x", "0", SyntaxError),
    ("x", "MyFunc(b)", NameError),  # note: when lhs is a vector, rhs is evaluated at construction
    ("x", "_b", NameError),
    ("x[1:]", "_b", NameError),
    ("x", "cos()", (TypeError, ValueError)),  # note: actual exception may depend on numpy version
    ("x", "cos(", SyntaxError),
    ("x[1:]", "ones(3)", ValueError),
    ("x", "ones(12)", ValueError),
    ("x", "ones(2)", ValueError),
    ("x[1:]", "[a, _b]", NameError),
    ("a", "_b", NameError),
    ("a", "MyFunc(b)", NameError),
    ("a", "_", NameError),
    ("x[1]", "MyFunc(b)", NameError),
    ("x[9]", "0.5", IndexError),
    ])
def test_AssignString__init__error(eval_context, lhs, rhs, exception):
    """Test expressions expected to raise an exception at instantiation"""
    with pytest.raises(exception):
        AssignString(lhs, rhs, eval_context)

@pytest.mark.parametrize("lhs, rhs, exception", [
    ("a", [1], TypeError),
    ("a", "[1]", TypeError),
    ("a", "(1, 2)", TypeError),
    ])
def test_AssignString_exec_error(eval_context, lhs, rhs, exception):
    """Test expressions expected to raise an exception at execution"""
    s = AssignString(lhs, rhs, eval_context)
    with pytest.raises(exception):
        s.exec()


@pytest.mark.parametrize("lhs", ["inwards.a", "a"])
def test_AssignString_exec_a(eval_context, lhs):
    context = eval_context  # for convenience
    assert context is eval_context
    context.a = 0.123
    context.x = np.r_[0.1, 0.2, 0.3]

    rhs = 'b * x[0]'
    s = AssignString(lhs, rhs, context)
    assert s.lhs == lhs
    assert s.rhs == rhs
    assert str(s) == f"{lhs} = {rhs}"
    assert s.eval_context is context
    assert s.shape is None
    assert context.a == 0.123, "The creation of an AssignString should not cause any assignment"
    context.b = 3.14

    # first execution
    value, changed = s.exec()
    assert changed
    assert value == pytest.approx(0.314)
    with pytest.raises(NameError, match="'a' is not defined"):
        assert a == pytest.approx(value)
    assert context.a == pytest.approx(value)

    # second execution
    value, changed = s.exec()
    assert not changed
    assert value == pytest.approx(0.314)


@pytest.mark.parametrize("lhs", ["inwards.x", "x", "x[:]", "x[::]"])
@pytest.mark.parametrize("rhs, setup, expected", [
    ("array([a, b, -a])", {'a': 0.99, 'b': 3.14}, [0.99, 3.14, -0.99]),
    ("[a, b, -a]", {'a': 0.99, 'b': 3.14}, [0.99, 3.14, -0.99]),
    ("a", {'a': 0.99, 'b': 3.14}, np.full(3, 0.99)),
    ("8", {'a': 0.99, 'b': 3.14}, np.full(3, 8.0)),
    (8, {'a': 0.99, 'b': 3.14}, np.full(3, 8.0)),
    ([0.3, 0.2, 0.1], {}, [0.3, 0.2, 0.1]),
    ("[0.3, 0.2, 0.1]", {}, [0.3, 0.2, 0.1]),
    (np.r_[0.3, 0.2, 0.1], {}, [0.3, 0.2, 0.1]),
    # integer-valued rhs: should not change x.dtype
    ([0, 2, 1], {}, [0, 2, 1]),
    (np.ones(3, dtype=int), {}, [1, 1, 1]),
    ])
def test_AssignString_exec_full_array(eval_context, setup, lhs, rhs, expected):
    context = eval_context  # for convenience
    assert context is eval_context
    context.x = np.r_[0.1, 0.2, 0.3]
    assert context.x == pytest.approx([0.1, 0.2, 0.3])
    assert context.x.dtype is np.dtype(float)

    s = AssignString(lhs, rhs, context)
    assert s.shape == (3,)
    assert s.eval_context is context
    assert context.x == pytest.approx([0.1, 0.2, 0.3])

    # setup sytem values
    for name, value in setup.items():
        context[name] = value

    # first execution
    value, changed = s.exec()
    assert changed
    assert value == pytest.approx(expected)
    assert context.x == pytest.approx(expected)
    assert context.x.dtype is np.dtype(float)
    with pytest.raises(NameError, match="'x' is not defined"):
        assert x == pytest.approx(expected)

    # second execution
    value, changed = s.exec()
    assert not changed
    assert value == pytest.approx(expected)
    assert context.x == pytest.approx(expected)


def test_AssignString_array_copy(eval_context):
    """
    Check that an AssignString of the kind `array1 = array2`
    does not make array1 a reference to array2, but assigns a copy instead.
    """
    context = eval_context  # for convenience
    assert context is eval_context
    context.x = np.r_[0.1, 0.2, 0.3]
    context.y = np.zeros(3)

    s = AssignString('x', 'y', context)
    assert s.shape == (3,)
    assert s.eval_context is context
    assert context.x is not context.y

    value, changed = s.exec()
    assert changed
    assert context.x is not context.y
    assert np.array_equal(value, context.x)
    assert np.array_equal(value, context.y)


@pytest.mark.parametrize("lhs, rhs, setup, expected", [
    ("x[::2]", "[a, b]", {'a': 0.99, 'b': 3.14}, [0.99, 0, 3.14]),
    ("x[[0, 2]]", "[a, b]", {'a': 0.99, 'b': 3.14}, [0.99, 0, 3.14]),
    ("x[1:]", "[a, b]", {'a': 0.99, 'b': 3.14}, [0, 0.99, 3.14]),
    ("x[[2, 0, 1]]", "[a, a + 1, a + 2]", {'a': 0.5}, [1.5, 2.5, 0.5]),
    ("x[1:2]", 8, {'a': 0.99, 'b': 3.14}, [0, 8, 0]),
    ("x[1:2]", "8", {'a': 0.99, 'b': 3.14}, [0, 8, 0]),
    ("x[:-1]", "a + b", {'a': 0.99, 'b': 3.14}, [4.13, 4.13, 0]),
    ("x[::2]", np.r_[-2.6, 0.66], {}, [-2.6, 0, 0.66]),
])
def test_AssignString_exec_masked_array(eval_context, setup, lhs, rhs, expected):
    context = eval_context  # for convenience
    assert context is eval_context
    context.x = np.zeros(3)
    assert context.x == pytest.approx([0, 0, 0])

    s = AssignString(lhs, rhs, context)
    assert s.shape is not None
    assert s.eval_context is context
    assert context.x == pytest.approx([0, 0, 0])

    # setup sytem values
    for name, value in setup.items():
        context[name] = value

    # first execution
    value, changed = s.exec()
    assert changed
    assert context.x == pytest.approx(expected)
    with pytest.raises(NameError, match="'x' is not defined"):
        assert x == pytest.approx(expected)

    # second execution
    value, changed = s.exec()
    assert not changed
    assert context.x == pytest.approx(expected)


def test_AssignString_rhs(eval_context):
    context = eval_context
    s = AssignString("sub.in_.q", 0, context)
    assert s.rhs == "0"
    context.sub.in_.q = 2.3
    value, changed = s.exec()
    assert changed
    assert context.sub.in_.q == 0

    s.rhs = "-cos(a)"
    context.a = 1.0
    assert context.sub.in_.q == 0
    value, changed = s.exec()
    assert changed
    assert context.sub.in_.q == -np.cos(1.0)
    context.a = 0.0
    value, changed = s.exec()
    assert changed
    assert context.sub.in_.q == pytest.approx(-1.0)

    with pytest.raises(NameError, match="'foo' is not defined"):
        s.rhs = "2 * foo.bar"

    with pytest.raises(SyntaxError):
        s.rhs = "2 * sin("


@pytest.mark.parametrize("lhs, rhs, expected", [
    ("a", "b", False),
    ("a", "0", True),
    ("a", "cos(pi)", True),
    ("x[1]", "1 + a", False),
    ("x[1]", "1 + a - a", False),
    ("x", "[1, 2, 3]", True),
    ("x", "[1, 2, a]", False),
])
def test_AssignString_constant(eval_context, lhs, rhs, expected):
    """Test whether rhs of assignment is a constant expression"""
    s = AssignString(lhs, rhs, eval_context)
    assert s.constant == expected


def test_AssignString_exec_changed_full_array(eval_context):
    context = eval_context  # for convenience
    assert context is eval_context
    context.x = np.zeros(3)
    assert context.x == pytest.approx([0, 0, 0])

    s = AssignString("x", "[a, a + b, b]", context)
    assert s.shape == (3,)
    assert s.eval_context is context
    assert context.x == pytest.approx([0, 0, 0])

    # setup sytem values
    setup = {'a': 0.99, 'b': 3.14}
    for name, value in setup.items():
        context[name] = value

    # first execution
    value, changed = s.exec()
    assert changed
    assert context.x == pytest.approx([0.99, 4.13, 3.14])
    assert value == pytest.approx(context.x)

    # second execution
    value, changed = s.exec()
    assert not changed
    assert context.x == pytest.approx([0.99, 4.13, 3.14])
    assert value == pytest.approx(context.x)

    # third execution
    context.x[1] = 0  # change x outside of AssignString s
    assert context.x == pytest.approx([0.99, 0, 3.14])
    value, changed = s.exec()
    assert changed
    assert context.x == pytest.approx([0.99, 4.13, 3.14])
    assert value == pytest.approx(context.x)


def test_AssignString_exec_changed_masked_array(eval_context):
    context = eval_context  # for convenience
    assert context is eval_context
    context.x = np.zeros(3)
    assert context.x == pytest.approx([0, 0, 0])

    s = AssignString("x[::2]", "[a, b]", context)
    assert s.shape is not None
    assert s.eval_context is context
    assert context.x == pytest.approx([0, 0, 0])

    # setup sytem values
    setup = {'a': 0.99, 'b': 3.14}
    for name, value in setup.items():
        context[name] = value

    # first execution
    value, changed = s.exec()
    assert changed
    assert context.x == pytest.approx([0.99, 0, 3.14])

    # second execution
    context.x[1] = 2.4
    value, changed = s.exec()
    assert not changed  # Note: x[1] has changed, but s detects no changes on x[::2]
    assert context.x == pytest.approx([0.99, 2.4, 3.14])

    # Change a and the expression of s.rhs, such that the actual value is unchanged
    context.a = 0.33
    s.rhs = "[3 * a, b]"
    value, changed = s.exec()
    assert not changed
    assert context.x == pytest.approx([0.99, 2.4, 3.14])

    context.a = 0.15
    value, changed = s.exec()
    assert changed
    assert value == pytest.approx([0.45, 3.14])
    assert context.x == pytest.approx([0.45, 2.4, 3.14])

    context.set_clean(PortType.IN)
    value, changed = s.exec()
    assert not changed
    assert value == pytest.approx([0.45, 3.14])
    assert context.x == pytest.approx([0.45, 2.4, 3.14])
    assert context.is_clean(PortType.IN)  ### Assignment does *not* modify clean/dirty status

    context.set_clean(PortType.IN)
    context.x = np.zeros(3)  # change x outside of AssignString s
    assert not context.is_clean(PortType.IN)
    value, changed = s.exec()
    assert changed
    assert value == pytest.approx([0.45, 3.14])
    assert context.x == pytest.approx([0.45, 0, 3.14])

    context.x[::2] = np.ones(2)  # change x outside of AssignString s
    assert context.x == pytest.approx([1, 0, 1])
    value, changed = s.exec()
    assert changed
    assert value == pytest.approx([0.45, 3.14])
    assert context.x == pytest.approx([0.45, 0, 3.14])


@pytest.mark.parametrize("rhs, value", [
    ("0", 0),
    ("1 + 4", 5),
    ("1.23 / 10", 1.23 / 10),
    ("cos(pi)", np.cos(np.pi)),
    ("26 * pi / 180", 26 * np.pi / 180),
    ("exp(-1.5)", np.exp(-1.5)),
    ("log(2)", np.log(2)),
])
def test_AssignString_constant_evaluation(eval_context, rhs, value):
    """Test that constant expressions are evaluated before being stored"""
    s = AssignString("a", rhs, eval_context)
    assert s.constant
    assert s.rhs == rhs  # representation of rhs is unchanged
    assert str(s._AssignString__sides) == f"(a, {value})"  # actual value is stored in 'sides'


@pytest.mark.parametrize("lhs, rhs, variables, lhs_vars", [
    ("sub.z", "norm(x, inf)", {'x', 'sub.z'}, {'sub.z'}),
    ("out.q", "g * cos(pi * x)", {'x', 'out.q'}, {'out.q'}),
    ("out.q", "g * cos(pi * x) + sub.z", {'x', 'sub.z', 'out.q'}, {'out.q'}),
    ("a", "2 * a", {'a'}, {'a'}),
    # (
    #     "(x, out.q)", "[0, 0, B52.in_.q], g * cos(pi * x) + sub.z",  # tuple assignment
    #     {'x', 'sub.z', 'out.q', 'B52.in_.q'}, {'x', 'out.q'},
    # ),
])
def test_AssignString_variables(eval_context, lhs, rhs, variables, lhs_vars):
    s = AssignString(lhs, rhs, eval_context)
    assert s.lhs_variables == lhs_vars
    assert s.variables() == variables
    assert s.lhs_variables.issubset(s.variables())
