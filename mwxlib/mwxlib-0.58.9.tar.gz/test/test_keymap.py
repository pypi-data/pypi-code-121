import mwx
from mwx.framework import KeyCtrlInterfaceMixin


class Test(KeyCtrlInterfaceMixin):
    def __init__(self, *args, **kwargs):
        
        self.handler = mwx.FSM({0:{}})
        
        @self.define_key('* x')
        def test(v):
            print(v)
            v.Skip()
        
        self.define_key('* x', print)
        self.define_key('* y')


if __name__ == "__main__":
    test = Test()
    print(test.handler)
    mwx.deb()
