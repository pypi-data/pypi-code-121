import pytest
import logging

from cosapp.core import connectors
from cosapp.core.connectors import Connector, ConnectorError
from cosapp.ports.port import PortType, Port
from cosapp.systems import System
from cosapp.ports.units import UnitError
from cosapp.utils.testing import assert_keys

# <codecell>

fake = System('fake')

class PortWithNoOwner(Port):
    def setup(self):
        self.add_variable('a')
        self.add_variable('x', unit='m')

class APort(Port):
    def setup(self):
        self.add_variable('a')
        self.owner = fake

class AbcPort(Port):
    def setup(self):
        self.add_variable('a', 1.0, unit='mm')
        self.add_variable('b', 1.0, unit='K')
        self.add_variable('c', 1.0)
        self.owner = fake

class AbcdPort(Port):
    """Compatible with AbcPort, with extra variable 'd'."""
    def setup(self):
        self.add_variable('a', 1.0, unit='inch')
        self.add_variable('b', 1.0, unit='degF')
        self.add_variable('c', 1.0)
        self.add_variable('d', 1.0)
        self.owner = fake

class XPort(Port):
    def setup(self):
        self.add_variable('x', unit='m')
        self.owner = fake

class XMassPort(Port):
    def setup(self):
        self.add_variable('x', unit='kg')
        self.owner = fake

class YPort(Port):
    def setup(self):
        self.add_variable('y')
        self.owner = fake

class XYPort(Port):
    def setup(self):
        self.add_variable('x', unit='m')
        self.add_variable('y', unit='degC')
        self.owner = fake

class XYImperialPort(Port):
    def setup(self):
        self.add_variable('x', unit='ft')
        self.add_variable('y', unit='degF')
        self.owner = fake

class XYZPort(Port):
    def setup(self):
        self.add_variable('x')
        self.add_variable('y')
        self.add_variable('z', 'test')
        self.owner = fake

class P(Port):
    def setup(self):
        self.add_variable('v', 2, unit='m')
        self.add_variable('w', 4)
        self.owner = fake

class Q(Port):
    def setup(self):
        self.add_variable('x')
        self.add_variable('y')
        self.add_variable('z')
        self.owner = fake

class R(Port):
    def setup(self):
        self.add_variable('v')
        self.add_variable('w')
        self.add_variable('z')
        self.owner = fake

class T(Port):
    def setup(self):
        self.add_variable('v')
        self.add_variable('y')
        self.owner = fake

# <codecell>

@pytest.fixture(scope="function")
def ConnectorFactory():
    """Connector factory from construction settings"""
    def factory(port1, port2, name="p2_to_p1", mapping=lambda p1, p2: dict(zip(p1, p2))) -> Connector:
        return Connector(name, port1, port2, mapping(port1, port2))
    return factory


@pytest.mark.parametrize("settings, expected", [
    (
        dict(
            port1 = XPort('p1', PortType.IN),
            port2 = XPort('p2', PortType.OUT),
            mapping = lambda p1, p2: 'x',
        ),
        dict(mapping={'x': 'x'}, conversions={'x': (1, 0)})
    ),
    (
        dict(
            port1 = XPort('p1', PortType.IN),
            port2 = YPort('p2', PortType.OUT),
            mapping = lambda p1, p2: {'x': 'y'},
        ),
        dict(mapping={'x': 'y'}, conversions={'x': (1, 0)})
    ),
    (
        dict(
            port1 = XYPort('p1', PortType.IN),
            port2 = XYPort('p2', PortType.OUT),
            mapping = lambda p1, p2: list(p2),
        ),
        dict(mapping={'x': 'x', 'y': 'y'}, conversions={'x': (1, 0), 'y': (1, 0)})
    ),
    (
        dict(
            port1 = XYPort('p1', PortType.IN),
            port2 = P('p2', PortType.OUT),
            mapping = lambda p1, p2: dict(zip(p1, p2)),
        ),
        dict(mapping={'x': 'v', 'y': 'w'}, conversions={'x': (1, 0), 'y': (1, 0)})
    ),
    (
        dict(
            port1 = Q('p1', PortType.IN),
            port2 = XYPort('p2', PortType.OUT, {'x': 2, 'y': 4}),
            mapping = lambda p1, p2: list(p2),
        ),
        dict(mapping={'x': 'x', 'y': 'y'}, conversions={'x': (1, 0), 'y': (1, 0)})
    ),
    (
        dict(
            port1 = XYPort('p1', PortType.IN, {'x': 1, 'y': 2}),
            port2 = R('p2', PortType.OUT, {'v': 2, 'w': 4, 'z': 3}),
            mapping = lambda p1, p2: dict(zip(p1, ['w', 'z'])),
        ),
        dict(mapping={'x': 'w', 'y': 'z'}, conversions={'x': (1, 0), 'y': (1, 0)})
    ),
    (
        dict(
            port1 = Q('p1', PortType.IN, {'x': 1, 'y': 2, 'z': 3}),
            port2 = R('p2', PortType.OUT, {'v': 2, 'w': 4, 'z': 3}),
            mapping = lambda p1, p2: 'z',
        ),
        dict(mapping={'z': 'z'})
    ),
    (
        dict(
            port1 = Q('p1', PortType.IN, {'x': 1, 'y': 2, 'z': 3}),
            port2 = R('p2', PortType.OUT, {'v': 2, 'w': 4, 'z': 3}),
            mapping = lambda p1, p2: {'x': 'w'},
        ),
        dict(mapping={'x': 'w'})
    ),
    (
        dict(
            port1 = T('p1', PortType.IN, {'v': 1, 'y': 2}),
            port2 = P('p2', PortType.OUT, {'v': 2, 'w': 4}),
            mapping = lambda p1, p2: ['v', 'foo'],
        ),
        dict(error=ConnectorError, match="variable 'foo' does not exist in port P")
    ),
    (
        dict(
            port1 = XYPort('p1', PortType.IN, {'x': 1, 'y': 2}),
            port2 = P('p2', PortType.OUT, {'v': 2, 'w': 4}),
            mapping = lambda p1, p2: {'x': 'v', 'foo': 'w'},
        ),
        dict(error=ConnectorError, match="variable 'foo' does not exist in port XYPort")
    ),
    (
        dict(
            port1 = AbcPort('p1', PortType.IN),
            port2 = AbcdPort('p2', PortType.OUT),
            mapping = lambda p1, p2: None,
        ),
        dict(mapping={k: k for k in list('abc')}, conversions={'a': (25.4, 0), 'b': (5/9, 459.67), 'c': (1, 0)})
    ),
    (
        dict(
            port1 = XYPort('p1', PortType.IN),
            port2 = XYImperialPort('p2', PortType.OUT),
            mapping = lambda p1, p2: 'y',
        ),
        dict(mapping={'y': 'y'}, conversions={'y': (5/9, -32)})
    ),
    (
        dict(
            port1 = XYPort('p1', PortType.IN),
            port2 = XYImperialPort('p2', PortType.OUT),
            mapping = lambda p1, p2: ['x', 'y'],
        ),
        dict(mapping={'x': 'x', 'y': 'y'}, conversions={'x': (0.3048, 0), 'y': (5/9, -32)})
    ),
    (
        dict(
            port1 = XPort('p1', PortType.IN),
            port2 = XMassPort('p2', PortType.OUT),
            mapping = lambda p1, p2: 'x',
        ),
        dict(error=UnitError, match="Unit m is not compatible with kg")
    ),
    (
        dict(
            port1 = XPort('p1', PortType.IN),
            port2 = PortWithNoOwner('p2', PortType.OUT),
            mapping = lambda p1, p2: {'x': 'a'},
        ),
        dict(error=ConnectorError, match="Source owner is undefined")
    ),
    (
        dict(
            port1 = PortWithNoOwner('p1', PortType.OUT),
            port2 = XPort('p2', PortType.IN),
            mapping = lambda p1, p2: {'a': 'x'},
        ),
        dict(error=ConnectorError, match="Sink owner is undefined")
    ),
    (
        dict(port1={'p1': PortType.OUT}, port2=XPort('p2', PortType.IN)),
        dict(error=TypeError, match="sink")
    ),
    (
        dict(port2={'p2': PortType.IN}, port1=XPort('p1', PortType.OUT)),
        dict(error=TypeError, match="source")
    ),
])
def test_Connector__init__(ConnectorFactory, settings, expected):
    error = expected.get('error', None)

    if error is None:
        c = ConnectorFactory(**settings)
        assert c.name == settings.get('name', 'p2_to_p1')
        assert c.sink is settings['port1']
        assert c.source is settings['port2']
        assert c.mapping == expected['mapping']
        # conversion factors:
        conversions = expected.get('conversions',
            { var: (1, 0) for var in expected['mapping']})
        assert_keys(c._unit_conversions, *conversions.keys())
        for var, values in conversions.items():
            assert c._unit_conversions[var] == pytest.approx(values, rel=1e-15), f"var = {var!r}"

    else:
        pattern = expected.get('match', None)
        with pytest.raises(error, match=pattern):
            c = ConnectorFactory(**settings)


def test_Connector_source_unit():
    """Check that changing 'source' updates the conversion table"""
    p1 = XYPort('p1', PortType.IN, {'x': -2, 'y': 0})
    p2 = AbcPort('p2', PortType.OUT, {'a': 1, 'b': 100, 'c': 0})
    c = Connector('p2_to_p1', p1, p2, {'x': 'a', 'y': 'b'})
    assert c.source is p2
    assert c.sink is p1
    conversion = c._unit_conversions
    assert_keys(conversion, 'x', 'y')
    assert conversion['x'] == pytest.approx((1e-3, 0), rel=1e-14)
    assert conversion['y'] == pytest.approx((1, -273.15), rel=1e-14)

    # Change source
    c.source = port = AbcdPort('port', PortType.IN)

    assert c.source is port
    assert conversion['x'] == pytest.approx((0.0254, 0), rel=1e-14)
    assert conversion['y'] == pytest.approx((5/9, -32), rel=1e-14)


def test_Connector_sink_unit():
    """Check that changing 'sink' updates the conversion table"""
    p1 = XYPort('p1', PortType.IN, {'x': -2, 'y': 0})
    p2 = AbcPort('p2', PortType.OUT, {'a': 1, 'b': 100, 'c': 0})
    c = Connector('p2_to_p1', p1, p2, {'x': 'a', 'y': 'b'})
    assert c.source is p2
    assert c.sink is p1
    conversion = c._unit_conversions
    assert_keys(conversion, 'x', 'y')
    assert conversion['x'] == pytest.approx((1e-3, 0), rel=1e-14)
    assert conversion['y'] == pytest.approx((1, -273.15), rel=1e-14)

    # Change source
    c.sink = port = XYImperialPort('port', PortType.IN)

    assert c.sink is port
    assert conversion['x'] == pytest.approx((1/304.8, 0), rel=1e-14)
    assert conversion['y'] == pytest.approx((1.8, -2298.35 / 9), rel=1e-14)


@pytest.mark.parametrize("settings, expected", [
    (
        dict(
            port1 = XYPort('p1', PortType.IN, {'x': 1, 'y': 2}),
            port2 = P('p2', PortType.OUT, {'v': 2, 'w': 4}),
        ),
        # expected output:
        dict(conversions={'x': (1, 0), 'y': (1, 0)},
            message="Connector source 'fake.p2.w' is dimensionless, but target 'fake.p1.y' has physical unit degC")
    ),
    (
        dict(
            port1 = P('p2', PortType.OUT, {'v': 2, 'w': 4}),
            port2 = XYPort('p1', PortType.IN, {'x': 1, 'y': 2}),
        ),
        dict(conversions={'v': (1, 0), 'w': (1, 0)},
            message="Connector source 'fake.p1.y' has physical unit degC, but target 'fake.p2.w' is dimensionless")
    ),
    (
        dict(
            port1 = XYZPort('p3', PortType.IN, {'x': 1, 'y': 2, 'z': 'test'}),
            port2 = XYZPort('p3', PortType.IN, {'x': 10, 'y': 20, 'z': 'test2'}),
        ),
        dict(conversions={'x': (1, 0), 'y': (1, 0), 'z': None})
    ),
])
def test_Connector_update_unit_conversion(caplog, ConnectorFactory, settings, expected):
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=connectors.__name__):
        c = ConnectorFactory(**settings)
        assert c._unit_conversions == expected['conversions']

    records = caplog.records
    expected_msg = expected.get('message', None)
    if expected_msg is None:
        assert len(records) == 0
    else:
        assert len(records) == 1
        assert expected_msg in records[-1].message


def test_Connector_transfer():
    p1 = XYPort('p1', PortType.IN, {'x': 1, 'y': 2})
    p2 = P('p2', PortType.OUT, {'v': 2, 'w': 4})
    c = Connector('p2_to_p1', p1, p2, dict(zip(p1, p2)))
    assert p1.x == 1
    assert p1.y == 2
    c.transfer()
    assert p1.x == 2  # Neutral unit conversion
    assert p1.y == 4  # No unit conversion

    p1 = XYPort('p1', PortType.IN)
    p2 = XYImperialPort('p2', PortType.OUT)
    c = Connector('p2_to_p1', p1, p2, ['x', 'y'])
    p2.x = 10.
    p2.y = 100.
    assert p1.x == 1
    assert p1.y == 1
    c.transfer()
    assert p1.x == pytest.approx(10 * 0.3048, rel=1e-15)
    assert p1.y == pytest.approx(5 / 9 * (100 - 32), rel=1e-15)
