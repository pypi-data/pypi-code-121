import pytest

import numpy as np

from cosapp.core.numerics.boundary import AbstractTimeUnknown, TimeUnknown
from cosapp.core.eval_str import EvalString
from cosapp.systems import System
from cosapp.drivers.time.utils import TimeUnknownDict


# class DummyTimeUnknown(AbstractTimeUnknown):
#     def __init__(self, context, der, max_time_step=np.inf):
#         self.context = context
#         self.__der = EvalString(der, context)
#         self.__max_dt = EvalString(max_time_step, context)

#     @property
#     def der(self) -> EvalString:
#         """Expression of the time derivative, given as an EvalString"""
#         return self.__der

#     @property
#     def max_time_step_expr(self) -> EvalString:
#         """Expression of the maximum admissible time step, given as an EvalString."""
#         return self.__max_dt

#     def reset(self):
#         """Reset transient unknown to a reference value"""
#         pass


class SubSystem(System):
    def setup(self):
        self.add_inward('x', 1.0)
        self.add_inward('y', np.ones(3))


class DummySystem(System):
    def setup(self):
        self.add_child(SubSystem('sub1'))
        self.add_child(SubSystem('sub2'))

        self.add_inward('f', 0.0)


@pytest.fixture(scope="function")
def system():
    return DummySystem("system")


@pytest.fixture(scope="function")
def unknowns(system):
    """Returns a list of dummy unknowns"""
    a = TimeUnknown(system, "f", der=0.5)
    b = TimeUnknown(system, "sub1.y", der="sub1.x")
    c = TimeUnknown(system, "sub2.x", der="sub1.y**2", max_time_step="0.1 * sub1.x")
    return a, b, c


@pytest.fixture(scope="function")
def unknowns_dict(unknowns):
    a, b, c = unknowns
    return unknowns, TimeUnknownDict(A=a, B=b, C=c)


@pytest.mark.parametrize("mapping, expected", [
    (dict(), dict()),
    (dict(foo="bar"), dict(error=TypeError, match="invalid item 'foo': str")),
])
def test_TimeUnknownDict__init__(mapping, expected):
    error = expected.get('error', None)

    if error is None:
        vardict = TimeUnknownDict(**mapping)
        assert len(vardict) == expected.get('length', 0)
    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            TimeUnknownDict(**mapping)


def test_TimeUnknownDict_getset(unknowns):
    """Test __getitem__ et __setitem__ methods"""
    a, b, c = unknowns

    vardict = TimeUnknownDict(A=a, B=b)
    assert set(vardict.keys()) == {"A", "B"}
    assert vardict["A"] is a
    assert vardict["B"] is b

    vardict["C"] = c
    assert set(vardict.keys()) == {"A", "B", "C"}
    assert vardict["C"] is c

    vardict["C2"] = c
    assert set(vardict.keys()) == {"A", "B", "C", "C2"}
    assert vardict["C2"] is c

    # Bad key in __getitem__
    with pytest.raises(KeyError):
        vardict["foo"]

    # Bad key in __setitem__
    with pytest.raises(TypeError, match="invalid key 0"):
        vardict[0] = a

    # Bad value in __setitem__
    with pytest.raises(TypeError, match="invalid item 'foo': str"):
        vardict["foo"] = "bar"

    with pytest.raises(TypeError, match="invalid item 'foo': int"):
        vardict["foo"] = 0


def test_TimeUnknownDict__len__(unknowns):
    a, b, c = unknowns

    vardict = TimeUnknownDict(A=a, B=b)
    assert len(vardict) == 2
    vardict["C"] = c
    assert len(vardict) == 3

    assert len(TimeUnknownDict()) == 0
    assert len(TimeUnknownDict(A=a)) == 1
    assert len(TimeUnknownDict(A=a, B=b)) == 2
    assert len(TimeUnknownDict(A=a, B=b, C=c)) == 3


def test_TimeUnknownDict_update(system, unknowns):
    a, b, c = unknowns

    vardict = TimeUnknownDict(A=a)
    assert set(vardict.keys()) == {"A"}

    vardict.update({"B": b, "C": c})
    assert set(vardict.keys()) == {"A", "B", "C"}

    d = TimeUnknown(system, 'sub2.y', der='f', max_time_step=0.1)
    other = TimeUnknownDict(D=d)
    vardict.update(other)
    assert vardict["D"] is d
    assert set(vardict.keys()) == {"A", "B", "C", "D"}
    assert set(vardict.values()) == {a, b, c, d}


def test_TimeUnknownDict_pop(unknowns):
    a, b, c = unknowns

    vardict = TimeUnknownDict(A=a, B=b, C=c)
    assert set(vardict.keys()) == {"A", "B", "C"}

    assert vardict.pop("B") is b
    assert set(vardict.keys()) == {"A", "C"}

    assert vardict.pop("foo", None) is None
    assert vardict.pop("foo", 3.14) == 3.14

    with pytest.raises(KeyError):
        vardict.pop("foo")


def test_TimeUnknownDict__contains__(unknowns_dict):
    unknowns, vardict = unknowns_dict
    assert set(vardict.keys()) == {"A", "B", "C"}
    assert "A" in vardict
    assert "B" in vardict
    assert "C" in vardict
    assert "D" not in vardict

    vardict.pop("B")
    assert "A" in vardict
    assert "B" not in vardict
    assert "C" in vardict


def test_TimeUnknownDict_clear(unknowns_dict):
    vardict = unknowns_dict[1]
    assert set(vardict.keys()) == {"A", "B", "C"}
    
    vardict.clear()
    assert set(vardict.keys()) == set()


def test_TimeUnknownDict_constrained(unknowns_dict):
    """Test property `constrained`"""
    (a, b, c), vardict = unknowns_dict
    constrained = vardict.constrained
    assert isinstance(constrained, dict)
    assert len(constrained) == 1
    assert set(constrained.keys()) <= set(vardict.keys())
    assert set(constrained.keys()) == {"C"}

    for key, value in constrained.items():
        assert value.constrained

    # Check that property is a shallow copy of an internal dict
    assert vardict.constrained.get("C") is c
    assert vardict.constrained.pop("C") is c
    assert set(vardict.constrained.keys()) == {"C"}  # key still present after pop


def test_TimeUnknownDict_iterators(unknowns_dict, system):
    """Test keys() and values() methods"""
    (a, b, c), vardict = unknowns_dict

    keys, values = [], []
    for key, value in vardict.items():
        assert isinstance(key, str)
        assert isinstance(value, AbstractTimeUnknown)
        keys.append(key)
        values.append(value)

    assert len(vardict) == 3
    assert len(keys) == len(vardict)
    assert len(values) == len(vardict)
    assert set(keys) == {"A", "B", "C"}
    assert set(values) == {a, b, c}

    assert set(vardict.keys()) == {"A", "B", "C"}
    assert set(vardict.values()) == {a, b, c}
    assert set(vardict.keys(constrained=True)) == {"C"}
    assert set(vardict.values(constrained=True)) == {c}

    vardict["C2"] = vardict["C"]
    assert vardict["C2"] is c
    assert set(vardict.keys()) == {"A", "B", "C", "C2"}
    assert set(vardict.values()) == {a, b, c}
    assert set(vardict.keys(constrained=True)) == {"C", "C2"}
    assert set(vardict.values(constrained=True)) == {c}

    vardict["C2"] = vardict["A"]
    assert vardict["C2"] is a
    assert set(vardict.keys()) == {"A", "B", "C", "C2"}
    assert set(vardict.values()) == {a, b, c}
    assert set(vardict.keys(constrained=True)) == {"C"}
    assert set(vardict.values(constrained=True)) == {c}

    # Add new time unknown
    d = TimeUnknown(system, 'sub2.y', der='f', max_time_step=0.1)
    vardict["D"] = d
    assert set(vardict.keys()) == {"A", "B", "C", "C2", "D"}
    assert set(vardict.values()) == {a, b, c, d}
    assert set(vardict.keys(constrained=True)) == {"C", "D"}
    assert set(vardict.values(constrained=True)) == {c, d}
    # Check property `constrained`
    assert isinstance(vardict.constrained, dict)
    assert set(vardict.keys(constrained=True)) == set(vardict.constrained.keys())
    assert set(vardict.values(constrained=True)) == set(vardict.constrained.values())


def test_TimeUnknownDict_max_time_step(unknowns_dict):
    unknowns, vardict = unknowns_dict
    assert set(vardict.keys()) == {"A", "B", "C"}
    
    s = vardict["C"].context
    s.sub1.x = 3
    s.sub1.y = np.r_[1.2, 0]
    s.sub2.x = 0
    s.sub2.y[:] = 0

    dt = vardict.max_time_step()
    assert dt == min(var.max_time_step for var in unknowns)
    assert dt == pytest.approx(0.3, rel=1e-15)

    s.sub1.x = -0.5
    with pytest.raises(RuntimeError, match="maximum time step of C was evaluated to non-positive value -0.05"):
        vardict.max_time_step()
    