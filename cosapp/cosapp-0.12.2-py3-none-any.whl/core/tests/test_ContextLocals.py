import pytest

from cosapp.core.eval_str import ContextLocals
from cosapp.systems.system import System


def test_ContextLocals___init___():
    a = System('dummy')
    local = ContextLocals(a)
    assert len(local) == 0
    assert local.context is a


def test_ContextLocals_missing_keys_success():
    class Dummy(System):
        def setup(self):
            self.add_inward('x', 1)
        
        def hello(self):
            print('hello')

    a = Dummy('dummy')
    local = ContextLocals(a)
    assert len(local) == 0
    assert local['x'] == a.x
    assert len(local) == 1
    assert local['hello'] == a.hello
    assert len(local) == 2
    assert set(local.keys()) == set(('x', 'hello'))


def test_ContextLocals_missing_keys_failure():
    a = System('dummy')
    local = ContextLocals(a)

    with pytest.raises(KeyError):
        local['a']
