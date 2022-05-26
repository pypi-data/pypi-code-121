import pytest
import logging
import re
import weakref
import itertools
from typing import MappingView
from unittest import mock
from contextlib import nullcontext as does_not_raise

from cosapp.core.module import Module
from cosapp.core.signal import Slot
from cosapp.drivers import Driver
from cosapp.utils.logging import LogFormat, LogLevel
from cosapp.utils.testing import no_exception


@pytest.fixture(autouse=True)
def PatchModule():
    """Patch Module to make it instanciable for tests"""
    patcher = mock.patch.multiple(
        Module,
        __abstractmethods__ = set(),
        is_standalone = lambda self: False,
    )
    patcher.start()
    yield
    patcher.stop()


@pytest.fixture(autouse=True)
def Russian_dolls():
    def factory(name: str, *submodules: str):
        head = Module(name)
        module_list = [head]
        last = head
        for name in submodules:
            last = last.add_child(Module(name))
            module_list.append(last)
        return module_list

    return factory


@pytest.fixture(scope="function")
def fake():
    return Module("fake")


@pytest.fixture
def composite():
    """Generates test module tree:

                 a
         ________|________
        |        |        |
       aa       ab        ac
      __|__           ____|____
     |     |         |    |    |
    aaa   aab       aca  acb  acc
    """
    def add_children(module, names):
        prefix = module.name
        for name in names:
            module.add_child(Module(f"{prefix}{name}"))

    a = Module('a')
    add_children(a, list('abc'))
    add_children(a.aa, list('ab'))
    add_children(a.ac, list('abc'))

    return a


@pytest.mark.parametrize("name, error", [
    ("a", None),
    ("A", None),
    ("foobar", None),
    ("foo4bar", None),
    ("loveYou2", None),
    ("CamelBack", None),
    ("foo_bar", None),
    ("foobar_", None),
    ("_foobar", ValueError),
    ("foo bar", ValueError),
    ("foobar?", ValueError),
    ("foo.bar", ValueError),
    ("foo:bar", ValueError),
    ("foo/bar", ValueError),
    ("1foobar", ValueError),
    ("foobar-2", ValueError),
    ("foobar:2", ValueError),
    ("foobar.2", ValueError),
    ("foo.bar", ValueError),
    ("inwards", ValueError),
    ("outwards", ValueError),
    (23, TypeError),
    (1.0, TypeError),
    (dict(a=True), TypeError),
    (list(), TypeError),
])
def test_Module__init__(name, error):
    if error is None:
        module = Module(name)
        assert module.name == name
    else:
        with pytest.raises(error):
            Module(name)


def test_Module__weakref__(fake):
    with no_exception():
        proxy = weakref.proxy(fake)


def test_Module_name_setter():
    module = Module("foo")
    assert module.name == "foo"
    module.name = "bar"
    assert module.name == "bar"
    with pytest.raises(ValueError):
        module.name = "invalid.name"


def test_Module_contextual_name(Russian_dolls):
    a, b, c, d = Russian_dolls(*iter('abcd'))

    assert a.contextual_name == ""
    assert b.contextual_name == "b"
    assert c.contextual_name == "b.c"
    assert d.contextual_name == "b.c.d"


def test_Module_fullname(Russian_dolls):
    a, b, c, d = Russian_dolls(*iter('abcd'))

    assert a.full_name(trim_root=True) == ""
    assert b.full_name(trim_root=True) == "b"
    assert c.full_name(trim_root=True) == "b.c"
    assert d.full_name(trim_root=True) == "b.c.d"

    assert a.full_name() == "a"
    assert b.full_name() == "a.b"
    assert c.full_name() == "a.b.c"
    assert d.full_name() == "a.b.c.d"


def test_Module_path(Russian_dolls):
    a, b, c, d = Russian_dolls(*iter('abcd'))

    assert a.path() == [a]
    assert b.path() == [a, b]
    assert c.path() == [a, b, c]
    assert d.path() == [a, b, c, d]


def test_Module_root(Russian_dolls):
    a, b, c, d = Russian_dolls(*iter('abcd'))

    assert a.root() is a
    assert b.root() is a
    assert c.root() is a
    assert d.root() is a


def test_Module_path_namelist(Russian_dolls):
    a, b, c, d = Russian_dolls(*iter('abcd'))

    assert a.path_namelist() == ["a"]
    assert b.path_namelist() == ["a", "b"]
    assert c.path_namelist() == ["a", "b", "c"]
    assert d.path_namelist() == ["a", "b", "c", "d"]


def test_Module_compute_calls():
    m = Module("m")

    assert m.compute_calls == 0

    m.run_once()
    assert m.compute_calls == 1

    m.call_setup_run()  # Reset counter
    assert m.compute_calls == 0


def test_Module_size():
    s = Module("s")
    T = Module("T")
    u = Module("u")
    v = Module("v")

    s.add_child(T)
    T.add_child(u)
    T.add_child(v)
    s.add_child(Module("r"))

    assert s.size == 5
    assert u.size == 1
    assert T.size == 3


def test_Module_get_path_to_child(Russian_dolls):
    a, b, c, d = Russian_dolls("a", "b", "c", "d")

    assert a.get_path_to_child(a) == ""
    assert a.get_path_to_child(b) == "b"
    assert a.get_path_to_child(c) == "b.c"
    assert a.get_path_to_child(d) == "b.c.d"
    assert b.get_path_to_child(c) == "c"
    assert b.get_path_to_child(d) == "c.d"

    with pytest.raises(ValueError, match="not a child of 'b'"):
        b.get_path_to_child(a)

    orphan = Module('orphan')
    with pytest.raises(ValueError, match="not a child of 'a'"):
        a.get_path_to_child(orphan)


def test_Module_pop_child_driver():
    # From Driver
    d = Driver("dummy")
    assert d.children == {}

    update = d.add_child(Driver("mydriver"))
    assert d.children == {"mydriver": update}

    d.pop_child("mydriver")
    assert d.children == {}

    with pytest.raises(AttributeError):
        d.pop_child("mydriver")


@pytest.mark.parametrize("child_name, values, expected", [
    (None, ['ab', 'ac', 'aa'], does_not_raise()),
    (None, ['aa', 'ac', 'ab'], does_not_raise()),
    (None, ('aa', 'ac', 'ab'), does_not_raise()),  # tuples work
    (None, {'aa', 'ac', 'ab'}, pytest.raises(TypeError,
        match="exec_order must be an ordered sequence")),  # sets fail
    (None, ['foo', 1, True], pytest.raises(ValueError,
        match="exec_order must be a permutation of \['aa', 'ab', 'ac'\]")),
    (None, ['aa', 'ac', 'aa', 'ab', 'ac', 'aa'],
        pytest.raises(ValueError, match="Repeated items \['aa', 'ac'\]")),
    ('aa', ['aab', 'aaa'], does_not_raise()),
    ('aa', ['aab', 'aaa', 'extra'], pytest.raises(ValueError)),  # too many elements
    ('aa', ['aab'], pytest.raises(ValueError)),  # too few elements
    ('ab', ['foo'], pytest.raises(ValueError, match="'ab' has no children")),
    ('ab', [], does_not_raise()),
])
def test_Module_exec_order(composite, child_name, values, expected):
    try:
        system = composite.children[child_name]
    except KeyError:
        system = composite

    with expected:
        system.exec_order = values
        assert isinstance(system.exec_order, MappingView)
        exec_order = list(system.exec_order)
        assert exec_order == list(values)
        assert exec_order == list(system.children)


@pytest.mark.parametrize("names", itertools.permutations(['aa', 'ab', 'ac']))
def test_Module_exec_order_perms(composite, names):
    composite.exec_order = names
    print(type(composite.exec_order))
    assert isinstance(composite.exec_order, MappingView)
    exec_order = list(composite.exec_order)
    assert exec_order == list(names)
    assert exec_order == list(composite.children)


def test_Module_setup_ran(fake):
    with mock.patch("cosapp.core.signal.signal.inspect"):
        fake_callback = mock.Mock(spec=lambda **kwargs: None)
        fake_callback.return_value = None

        fake.setup_ran.connect(Slot(fake_callback))
        fake.call_setup_run()

        fake_callback.assert_called_once_with()


def test_Module_computed(fake):
    with mock.patch("cosapp.core.signal.signal.inspect"):
        fake_callback = mock.Mock(spec=lambda **kwargs: None)
        fake_callback.return_value = None

        fake.computed.connect(Slot(fake_callback))
        fake.run_once()

        fake_callback.assert_called_once_with()


def test_Module_clean_ran(fake):
    with mock.patch("cosapp.core.signal.signal.inspect"):
        fake_callback = mock.Mock(spec=lambda **kwargs: None)
        fake_callback.return_value = None

        fake.clean_ran.connect(Slot(fake_callback))
        fake.call_clean_run()

        fake_callback.assert_called_once_with()


@pytest.mark.parametrize("format", LogFormat)
@pytest.mark.parametrize("msg, kwargs, to_log, emitted", [
    ("zombie call_setup_run", dict(), False, None),
    ("useless start call_clean_run", dict(activate=True), False, None),
    (f"{Module.CONTEXT_EXIT_MESSAGE} call_clean_run", dict(activate=False), False, dict(levelno=LogLevel.DEBUG, pattern=r"Compute calls for [\w\.]+: \d+")),
    ("common message", dict(), True, None),
])
def test_Module_log_debug_message(format, msg, kwargs, to_log, emitted):
    handler = mock.MagicMock(level=LogLevel.DEBUG, log=mock.MagicMock())
    rec = logging.getLogRecordFactory()("log_test", LogLevel.INFO, __file__, 22, msg, (), None)
    for key, value in kwargs.items():
        setattr(rec, key, value)
    
    m = Module("dummy")

    assert m.log_debug_message(handler, rec, format) == to_log

    if emitted:
        handler.log.assert_called_once()
        args = handler.log.call_args[0]
        assert args[0] == emitted["levelno"]
        assert re.match(emitted["pattern"], args[1]) is not None
    else:
        handler.log.assert_not_called()


def test_Module_tree_default(composite):
    names = [elem.name for elem in composite.tree()]
    assert names == [
        'aaa', 'aab', 'aa',
        'ab',
        'aca', 'acb', 'acc', 'ac',
        'a',
    ]


@pytest.mark.parametrize("downwards, expected", [
    (True,  ['a', 'aa', 'aaa', 'aab', 'ab', 'ac', 'aca', 'acb', 'acc']),
    (False, ['aaa', 'aab', 'aa', 'ab', 'aca', 'acb', 'acc', 'ac', 'a']),
])
def test_Module_tree(composite, downwards, expected):
    """Test top-to-bottom and bottom-to-top `Module.tree` generator"""
    names = [elem.name for elem in composite.tree(downwards)]
    assert names == expected


def test_Module_iter_tree(composite):
    a = composite
    elems = a.tree(downwards=True)
    assert next(elems) is a
    assert next(elems) is a.aa
    assert next(elems) is a.aa.aaa
    assert next(elems) is a.aa.aab
    assert next(elems) is a.ab
    # Check remaining elements
    assert [elem.name for elem in elems] == ['ac', 'aca', 'acb', 'acc']


@pytest.mark.parametrize("downwards, order, expected", [
    (True,  ['aa', 'ac', 'ab'], ['a', 'aa', 'aaa', 'aab', 'ac', 'aca', 'acb', 'acc', 'ab']),
    (True,  ['ac', 'ab', 'aa'], ['a', 'ac', 'aca', 'acb', 'acc', 'ab', 'aa', 'aaa', 'aab']),
    (False, ['aa', 'ac', 'ab'], ['aaa', 'aab', 'aa', 'aca', 'acb', 'acc', 'ac', 'ab', 'a']),
    (False, ['ac', 'ab', 'aa'], ['aca', 'acb', 'acc', 'ac', 'ab', 'aaa', 'aab', 'aa', 'a']),
])
def test_Module_tree_exec_order_top(composite, downwards, order, expected):
    """Check that `Module.tree` is consistent with `exec_order`"""
    composite.exec_order = order
    names = [elem.name for elem in composite.tree(downwards)]
    assert names == expected


def test_Module_tree_exec_order_sub(composite):
    """Check that `Module.tree` is consistent with `exec_order`"""
    a = composite
    names = lambda system, downwards=False: [s.name for s in system.tree(downwards)]

    a.exec_order = ('ac', 'ab', 'aa')
    assert names(a) == ['aca', 'acb', 'acc', 'ac', 'ab', 'aaa', 'aab', 'aa', 'a']

    a.aa.exec_order = ('aab', 'aaa')
    assert names(a) == ['aca', 'acb', 'acc', 'ac', 'ab', 'aab', 'aaa', 'aa', 'a']

    a.ac.exec_order = ('acb', 'acc', 'aca')
    assert names(a) == ['acb', 'acc', 'aca', 'ac', 'ab', 'aab', 'aaa', 'aa', 'a']
    assert names(a.aa) == ['aab', 'aaa', 'aa']
    assert names(a.ab) == ['ab']
    assert names(a.ac) == ['acb', 'acc', 'aca', 'ac']

    # Test downward iterator
    assert names(a, True) == ['a', 'ac', 'acb', 'acc', 'aca', 'ab', 'aa', 'aab', 'aaa']
    assert names(a.aa, True) == ['aa', 'aab', 'aaa']


def test_Module_tree_reverse(composite):
    """Check that changing `Module.tree` direction in a composite system
     does *not* produce a globally reversed iterator, owing to recursion.
    """
    downwards = list(composite.tree(downwards=True))
    upwards = list(composite.tree(downwards=False))

    assert upwards != list(reversed(downwards))
