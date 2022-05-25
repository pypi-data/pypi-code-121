from IutyLib.commonutil.convert import str2float

from IutyLib.coding.tdd import case
from IutyLib.coding.asserts import assertEqual

def add(a,b):
    return a+b

def pinus(a,b):
    return a-b

@case()
def test_add():
    v = add(5,9)
    assertEqual(v,14)

