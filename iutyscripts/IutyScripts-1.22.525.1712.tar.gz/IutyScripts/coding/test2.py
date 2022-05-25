from IutyLib.coding.tdd import setup,case
from IutyLib.coding.asserts import assertEqual,assertTrue,assertFalse
import importlib


from IutyLib.coding.tdd import ins_MethodTest, test_process
ins_MethodTest._testmode  = True

@case("a example of static test")
def test_import():
    m = setup("test8")
    
    assertTrue(not m is None,"import module success")
    pass

@case("a example of static test",mustpass=["test_import"])
def test_add():
    m = setup("test0")
    v = m.add(3,5)
    assertEqual(v,9)

lib = "test0"
importlib.__import__(lib)

test_process(r"d:/")