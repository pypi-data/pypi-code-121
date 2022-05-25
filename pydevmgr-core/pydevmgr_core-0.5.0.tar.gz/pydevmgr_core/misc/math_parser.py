import math
import ast
import operator as op


_operators2method = {
    ast.Add: op.add, 
    ast.Sub: op.sub, 
    ast.BitXor: op.xor, 
    ast.Or:  op.or_, 
    ast.And: op.and_, 
    ast.Mod:  op.mod,
    ast.Mult: op.mul,
    ast.Div:  op.truediv,
    ast.Pow:  op.pow,
    ast.FloorDiv: op.floordiv,              
    ast.USub: op.neg, 
    ast.UAdd: lambda a:a  
}

class DataEval:
    """ Basic parser with local variable and math functions 
    
    Args:
       vars (mapping): mapping object where obj[name] -> numerical value 
       math (bool, optional): if True (default) all math function are added in the same name space
       
    Example:
       
       data = {'r': 3.4, 'theta': 3.141592653589793}
       parser = DataEval(data)
       assert parser.parse('r*cos(theta)') == -3.4
       data['theta'] =0.0
       assert parser.parse('r*cos(theta)') == 3.4
    """
        
    
    
    def __init__(self, vars: dict, math=True):
        self._vars = vars
        if not math:
            self._alt_name = self._no_alt_name
        
            
    def _Name(self, name):
        try:
            return  self._vars[name]
        except KeyError:
            return self._alt_name(name)
                
    @staticmethod
    def _alt_name(name):
        if name.startswith("_"):
            raise NameError(f"{name!r}") 
        try:
            return  getattr(math, name)
        except AttributeError:
            raise NameError(f"{name!r}") 
    
    @staticmethod
    def _no_alt_name(name):
        raise NameError(f"{name!r}") 
    
    @staticmethod
    def Call(f,args):
        return f(*args)
    
    def eval_(self, node):
        if isinstance(node, ast.Expression):
            return self.eval_(node.body)
        if isinstance(node, ast.Num): # <number>
            return node.n
        if isinstance(node, ast.Name):
            return self._Name(node.id) 
        if isinstance(node, ast.BinOp):            
            method = _operators2method[type(node.op)]                      
            return method( self.eval_(node.left), self.eval_(node.right) )            
        if isinstance(node, ast.UnaryOp):             
            method = _operators2method[type(node.op)]  
            return method( self.eval_(node.operand) )
        if isinstance(node, ast.Attribute):
            return getattr(self.eval_(node.value), node.attr)
            
        if isinstance(node, ast.Call):            
            return self.eval_(node.func)( 
                      *(self.eval_(a) for a in node.args),
                      **{k.arg:self.eval_(k.value) for k in node.keywords}
                     )
        else:
            raise TypeError(node)
    
    def eval(self, expr):
        return  self.eval_(ast.parse(expr, mode='eval'))          
    



class ExpEval:
    """ Basic parser from a set of data
    
    Args:
       exp (str): expression to eval 
       math (bool, optional): if True (default) all math function are added in the same name space
       
    Example:
       
       
    """
    
    def __init__(self, exp: str, math=True):        
        self._exp = ast.parse(exp, mode='eval')                 
        if not math:
            self._alt_name = self._no_alt_name
        
            
    def _Name(self, name, vars):
        try:
            return vars[name]
        except KeyError:
            return self._alt_name(name)
                
    @staticmethod
    def _alt_name(name):
        if name.startswith("_"):
            raise NameError(f"{name!r}") 
        try:
            return  getattr(math, name)
        except AttributeError:
            raise NameError(f"{name!r}") 
    
    @staticmethod
    def _no_alt_name(name):
        raise NameError(f"{name!r}") 
    
    @staticmethod
    def Call(f,args):
        return f(*args)
    
    def eval_(self, node, vars):
        if isinstance(node, ast.Expression):
            return self.eval_(node.body, vars)
        if isinstance(node, ast.Num): # <number>
            return node.n
        if isinstance(node, ast.Name):
            return self._Name(node.id, vars) 
        if isinstance(node, ast.BinOp):            
            method = _operators2method[type(node.op)]                      
            return method( self.eval_(node.left, vars), self.eval_(node.right, vars) )            
        if isinstance(node, ast.UnaryOp):             
            method = _operators2method[type(node.op)]  
            return method( self.eval_(node.operand, vars) )
        if isinstance(node, ast.Attribute):
            return getattr(self.eval_(node.value, vars), node.attr)
            
        if isinstance(node, ast.Call):            
            return self.eval_(node.func, vars)( 
                      *(self.eval_(a, vars) for a in node.args),
                      **{k.arg:self.eval_(k.value, vars) for k in node.keywords}
                     )                       
        else:
            raise TypeError(node)
    
    def eval(self, vars):
        return  self.eval_(self._exp, vars)      




if __name__=="__main__":    
    assert DataEval({"x":4.5}).eval('x*2') == 9
    assert DataEval({"x":4}).eval('cos(pi)') == -1.0
        
    data = {'r': 3.4, 'theta': 3.141592653589793}
    parser = DataEval(data)
    assert parser.eval('r*cos(theta)') == -3.4
    data['theta'] = 0.0
    assert parser.eval('r*cos(theta)') == 3.4
    assert DataEval(globals()).eval('math.pi') == math.pi
    
    assert DataEval({'f':lambda x,n=10: x*n}).eval('f(2,20)') == 40
    assert DataEval({'f':lambda x,n=10: x*n}).eval('f(2,n=20)') == 40  
    
    
    assert ExpEval('4*x').eval({'x':5}) == 20
      
    print("OK")