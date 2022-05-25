

from TestProxy import test as t
from TestProxy import setup,ins_MethodTest
from TestProxy import case,assertEqual,assertTrue

ins_MethodTest._testmode = True





@case()
def test_add():
    m = setup("test")
    v = m.add(1,1)
    assert v == 2
    #assert v == 3,"运算结果不正确"
    assertEqual(v,2)
    
    assertEqual(v,3,"not exactly")
    pass


class Demo:
    
    
    @case(msg="do test")
    def test_pinus(msg="do test"):
        m = setup("test")
        v = m.pinus(5,3)
        assertEqual(v,2.0,"type same?")
        
        assertTrue(1!=1,"1!=1")
        
t()