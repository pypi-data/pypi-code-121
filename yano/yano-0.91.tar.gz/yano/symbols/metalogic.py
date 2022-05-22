from ..data.iterate import iterate

class logic_obj(object):
    def evaluate(self,value):
        return bool(self.getvalue(value))
    def __call__(self,value):
        return self.evaluate(value)
    def __getitem__(self,value):
        return self.evaluate(value)
    
    def getvalue(self,value):
        assert False, f"Only a condition (not {type(self)}) can be evaluated"
        


    def __and__(self,other):
        return logic_and(self,other)
    
    def __or__(self,other):
        return logic_or(self,other)

    def __invert__(self):
        return logic_not(self)


    def __lt__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self, other, "below")

    def __gt__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self, other, "above")

    def __eq__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self, other, "equal")

    def __ne__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self, other, "not_equal")

    def __le__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self, other, "below_or_equal")

    def __ge__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self, other, "above_or_equal")

    def __sub__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self,other,"subtract")

    def __rsub__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(other,self,"subtract")

    def __add__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self,other,"add")

    def __radd__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(other,self,"add")

    def __mul__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self,other,"multiply")

    def __rmul__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(other,self,"multiply")

    def __truediv__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self,other,"divide")

    def __rtruediv__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(other,self,"divide")

    def __mod__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(self,other,"modulo")

    def __rmod__(self,other):
        assert type(other) is int or type(other) is float or type(other) is str or hasattr(other,"getvalue"), "Only numbers can be compared"
        return logic_condition(other,self,"modulo")

    def __iter__(self):
        return iterate(self)

    def count(self):
        return len(list(iterate(self)))
    
    def __len__(self):
        return self.count()




class logic_condition(logic_obj):
    def __init__(self, a, b, condition="below"):
        self.a = a
        self.b = b
        self.condition = condition

    def getvalue(self, value):
        assert type(value) is dict, "Evalution requires a dictionary of values"
        v1=self.a
        v2=self.b
        def refine(v):
            if hasattr(v,"getvalue"):
                return v.getvalue(value)
            elif v in value.keys():
                return value[v]
            elif type(v) is str or type(v) is int or type(v) is float:
                return v
            else:
                assert False, f"{v}({type(v)}) is not a valid value"
        v1=refine(v1)
        v2=refine(v2)
        #print("comparing",self.condition,self.a,"=",v1,"  ",self.b,"=",v2,"(",type(self.a),type(self.b),")")
        if self.condition == "below":
            return v1 < v2
        elif self.condition == "above":
            return v1 > v2
        elif self.condition == "equal":
            return v1 == v2
        elif self.condition == "not_equal":
            return v1 != v2
        elif self.condition == "below_or_equal":
            return v1 <= v2
        elif self.condition == "above_or_equal":
            return v1 >= v2
        elif self.condition == "subtract":
            return v1 - v2
        elif self.condition == "add":
            return v1 + v2
        elif self.condition == "multiply":
            return v1 * v2
        elif self.condition == "divide":
            return v1 / v2
        elif self.condition == "modulo":
            return v1 % v2
        else:
            assert False, f"Unknown condition {self.condition}"

    def __repr__(self):
        if self.condition == "below":
            return "{} < {}".format(self.a, self.b)
        elif self.condition == "above":
            return "{} > {}".format(self.a, self.b)
        elif self.condition == "equal":
            return "{} == {}".format(self.a, self.b)
        elif self.condition == "not_equal":
            return "{} != {}".format(self.a, self.b)
        elif self.condition == "below_or_equal":
            return "{} <= {}".format(self.a, self.b)
        elif self.condition == "above_or_equal":
            return "{} >= {}".format(self.a, self.b)
        elif self.condition == "subtract":
            return "{} - {}".format(self.a,self.b)
        elif self.condition == "add":
            return "{} + {}".format(self.a,self.b)
        elif self.condition == "multiply":
            return "{} * {}".format(self.a,self.b)
        elif self.condition == "divide":
            return "{} / {}".format(self.a,self.b)
        elif self.condition == "modulo":
            return "{} % {}".format(self.a,self.b)
        else:
            return "Unknown condition"

class logic_and(logic_obj):
    def __init__(self, *args):
        self.args = args

    def getvalue(self, value):
        for arg in self.args:
            if not arg.evaluate(value):
                return 0
        return 1

    def __repr__(self):
        return "("+(" and ".join([str(arg) for arg in self.args]))+")"

class logic_or(logic_obj):
    def __init__(self, *args):
        self.args = args

    def getvalue(self, value):
        for arg in self.args:
            if arg.evaluate(value):
                return 1
        return 0

    def __repr__(self):
        return "("+(" or ".join([str(arg) for arg in self.args]))+")"

class logic_not(logic_obj):
    def __init__(self,obj):
        self.obj=obj

    def getvalue(self,value):
        val=self.obj.evaluate(value)
        return 1-int(val)

    def __repr__(self):
        return "not "+str(self.obj)















class logic_variable(logic_obj):
    def __init__(self, name):
        self.name = name


    def getvalue(self, value):
        if self.name in value.keys():
            return value[self.name]
        else:
            return 0

    def __repr__(self):
        return self.name



def filter_data(data,condition):
    for x in data:
        if condition.evaluate(x):
            yield x





