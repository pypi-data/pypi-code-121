import unittest
import mwx
## from myutilus import inspect_args


## @inspect_args
def func(a, b, c=-1, v=None, *args, **kwargs):
    """Test func"""
    print("(a, b, c, v) =", (a, b, c, v))

## @inspect_args
def func2(a, b, c=-1, v=None, *args, key:int, value:int=0, **kwargs) -> int:
    """This function with new syntax"""
    print("(a, b, c, v) =", (a, b, c, v))

## @inspect_args
class A(object):
    """class doc:str
    """
    ## @inspect_args
    def call(self, a, b, c=-1, v=None, **kwargs):
        """method doc:str"""
        print("(a, b, c, v) =", (a, b, c, v), kwargs)


class TestUtilus(unittest.TestCase):
    
    def do_check(self, f, *args, **kwargs):
        _f = mwx.funcall(f, *args, **kwargs)
        print(f"$ {mwx.typename(_f)}({args=}, {kwargs=})")
        _f(0)
        _f(0, 1)
        _f(0, 1, 2)
    
    def test_function(self):
        a = A()
        f = a.call
        
        with self.assertRaises(TypeError):
            self.do_check(f)
        
        with self.assertRaises(TypeError):
            self.do_check(f, a=-1)
        
        with self.assertRaises(TypeError):
            self.do_check(f, b=-1)
        
        self.do_check(f, a=-1, b=-1, hoge=-1)
        self.do_check(f, -1)
        self.do_check(f, -1, -2) # call~
        self.do_check(f, -1, -2, -3) # call~
        self.do_check(f, -1, -2, v=-3) # call~
        self.do_check(f, -1, -2, -3, -4) # call~

        with self.assertRaises(TypeError):
            self.do_check(f, -1, -2, -3, -4, -5)

if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    a = A()
    f = a.call # funcall:function
    ## f = func
    
    _f = mwx.funcall(f, a=-1, b=-1, hoge=-1) # call~
    ## _f = mwx.funcall(f, a=-1) # NG
    ## _f = mwx.funcall(f, b=-1) # NG
    ## _f = mwx.funcall(f) # NG
    ## _f = mwx.funcall(f, -1) # ok
    ## _f = mwx.funcall(f, -1, -2) # call~
    ## _f = mwx.funcall(f, -1, -2, -3) # call~
    ## _f = mwx.funcall(f, -1, -2, c=-3) # call~
    ## _f = mwx.funcall(f, -1, -2, v=-3) # call~
    ## _f = mwx.funcall(f, -1, -2, -3, -4) # call~
    ## _f = mwx.funcall(f, -1, -2, -3, -4, -5) #-> TypeError: call() takes from 3 to 5 positional arguments but 6 were given
    
    ## inspect_args(f)
    ## inspect_args(_f)
    
    print("mwx.typename(_f) =", mwx.typename(_f))
    ## _f()
    _f(0)
    _f(0, 1)
    _f(0, 1, 2)
