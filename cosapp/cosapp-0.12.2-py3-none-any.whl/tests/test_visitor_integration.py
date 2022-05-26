import pytest
import itertools

from cosapp.patterns.visitor import Visitor, send
from cosapp.systems import System
from cosapp.drivers import RunOnce, NonLinearSolver, ValidityCheck
from cosapp.utils.testing import get_args
from cosapp.tests.library.ports import XPort, X3Port


class NameCollector(Visitor):
    """Visitor collecting entity names"""
    def __init__(self):
        self.data = dict(
            (key, list())
            for key in ('systems', 'ports', 'drivers')
        )
    
    def visit_port(self, port) -> None:
        self.data['ports'].append(port.name)
    
    def visit_system(self, system) -> None:
        self.data['systems'].append(system.name)
    
    def visit_driver(self, driver) -> None:
        self.data['drivers'].append(driver.name)


class DataCollector(Visitor):
    """Visitor collecting miscellaneous data"""
    def __init__(self):
        self.data = dict(
            (key, dict())
            for key in ('systems', 'ports', 'drivers')
        )
    
    def visit_port(self, port) -> None:
        key = port.contextual_name
        self.data['ports'][key] = len(port)
    
    def visit_system(self, system) -> None:
        key = system.full_name()
        self.data['systems'][key] = system.size
        ports = list(system.inputs.values()) + list(system.outputs.values())
        send(self, ports)
    
    def visit_driver(self, driver) -> None:
        key = type(driver).__name__
        attr = self.data['drivers']
        attr.setdefault(key, 0)
        attr[key] += 1


@pytest.fixture
def system_1():
    def add_children(system, names):
        prefix = system.name
        for name in names:
            system.add_child(System(f"{prefix}{name}"))

    a = System('a')
    add_children(a, list('abc'))
    add_children(a.aa, list('ab'))
    add_children(a.ac, list('abc'))

    return a


@pytest.mark.parametrize("downwards, expected", [
    (True,  ['a', 'aa', 'aaa', 'aab', 'ab', 'ac', 'aca', 'acb', 'acc']),
    (False, ['aaa', 'aab', 'aa', 'ab', 'aca', 'acb', 'acc', 'ac', 'a']),
])
def test_System_send_visitor(system_1, downwards, expected):
    a = system_1
    visitor = NameCollector()
    a.send_visitor(visitor, downwards)

    assert visitor.data['ports'] == []
    assert visitor.data['drivers'] == []
    assert visitor.data['systems'] == expected


def test_System_send_visitor_default(system_1):
    """Test default behaviour of `System.send_visitor`.
    """
    a = system_1
    visitor = NameCollector()
    a.send_visitor(visitor)

    names = [
        'aaa', 'aab', 'aa',
        'ab',
        'aca', 'acb', 'acc', 'ac',
        'a',
    ]

    assert visitor.data['ports'] == []
    assert visitor.data['drivers'] == []
    assert visitor.data['systems'] == names

    # Send data collector
    visitor = DataCollector()
    a.send_visitor(visitor)

    assert visitor.data['drivers'] == {}
    assert visitor.data['systems'] == {
        'a': 9,
        'a.aa': 3,
        'a.ab': 1,
        'a.ac': 4,
        'a.aa.aaa': 1,
        'a.aa.aab': 1,
        'a.ac.aca': 1,
        'a.ac.acb': 1,
        'a.ac.acc': 1,
    }
    port_data = {}
    port_data.update(
        (f"{name}.{p}wards", 0)
        for name, p in itertools.product(names, ('in', 'out'))
    )
    port_data.update(
        (f"{name}.modevars_{p}", 0)
        for name, p in itertools.product(names, ('in', 'out'))
    )
    assert visitor.data['ports'] == port_data


def test_visitor_send(system_1):
    """Same as `test_System_send_visitor`, using function `visitor.send`.
    """
    a = system_1
    visitor = NameCollector()
    send(visitor, a.tree())

    assert visitor.data['ports'] == []
    assert visitor.data['drivers'] == []
    assert visitor.data['systems'] == [
        'aaa', 'aab', 'aa',
        'ab',
        'aca', 'acb', 'acc', 'ac',
        'a',
    ]


def test_send_DataCollector(DummySystemFactory):
    """Send `DataCollector` visitor on composite system with drivers"""
    A = DummySystemFactory("A",
        inwards = [get_args('x', 1.0), get_args('y', 0.5)],
        outwards = [get_args('z', 0.0)],
        inputs = get_args(X3Port, 'p_in'),
        outputs = get_args(XPort, 'q_out'),
    )
    B = DummySystemFactory("B",
        inputs = get_args(X3Port, 'u'),
        outputs = get_args(X3Port, 'v'),
    )

    top = System('top')
    top.add_child(A('a'))
    top.add_child(B('b'))
    top.a.add_child(B('b'))

    top.add_driver(ValidityCheck('check'))
    top.a.add_driver(NonLinearSolver('solver'))
    top.b.add_driver(RunOnce('runner'))
    top.b.add_driver(ValidityCheck('check'))
    
    visitor = DataCollector()
    top.send_visitor(visitor)

    assert visitor.data['systems'] == {
        'top': 4,
        'top.a': 2,
        'top.b': 1,
        'top.a.b': 1,
    }
    port_data = {
        'top.inwards': 0,
        'top.outwards': 0,
        'b.inwards': 0,
        'b.outwards': 0,
        'a.inwards': 2,
        'a.outwards': 1,
        'a.p_in': 3,
        'a.q_out': 1,
        'b.u': 3,
        'b.v': 3,
    }
    names = [s.name for s in top.tree()]
    port_data.update(
        (f"{name}.modevars_{p}", 0)
        for name, p in itertools.product(names, ('in', 'out'))
    )
    assert visitor.data['ports'] == port_data
    assert visitor.data['drivers'] == {}

    for system in top.tree():
        for driver in system.drivers.values():
            send(visitor, driver.tree())

    assert visitor.data['drivers'] == {
        'NonLinearSolver': 1,
        'RunSingleCase': 1,
        'ValidityCheck': 2,
        'RunOnce': 1,
    }
