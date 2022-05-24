#!/usr/bin/env python
# coding: utf-8

# In[1]:


from cogent3.util.union_dict import UnionDict

data = UnionDict(a=2, b={"c": 24, "d": [25]})
data.a


# In[2]:


data["a"]


# In[3]:


data.b.d


# In[4]:


from cogent3.util.union_dict import UnionDict

data = UnionDict(a=2, b={"c": 24, "d": [25]})
data.b |= {"d": 25}
data.b


# In[5]:


data.b.union({"d": [25]})


# In[6]:


data.b
{"c": 24, "d": [25]}


# In[7]:


from cogent3.util.union_dict import UnionDict

data = UnionDict(a=2, b={"c": 24, "d": [25]})
data["k"]


# In[8]:


data.k


# In[9]:


import numpy

def DiffOmega(omega):
    def omega_from_S(S):
        omega_est = S / (1 - numpy.e ** (-1 * S))
        return abs(omega - omega_est) ** 2

    return omega_from_S

omega = 0.1
f = DiffOmega(omega)


# In[10]:


from cogent3.maths.optimisers import minimise, maximise

S = minimise(
    f,  # the function
    xinit=1.0,  # the initial value
    bounds=(-100, 100),  # [lower,upper] bounds for the parameter
    local=True,  # just local optimisation, not Simulated Annealing
    show_progress=False,
)
assert 0.0 <= f(S) < 1e-6
print("S=%.4f" % S)


# In[11]:


from cogent3.util.misc import iterable

my_var = 10
for i in my_var:
    print("will not work")

for i in iterable(my_var):
    print(i)


# In[12]:


from cogent3.util.misc import curry

def foo(x, y):
    """Some function"""
    return x + y

bar = curry(foo, 5)
print(bar.__doc__)
bar(10)


# In[13]:


from cogent3.util.misc import is_iterable

can_iter = [1, 2, 3, 4]
cannot_iter = 1.234
is_iterable(can_iter)


# In[14]:


is_iterable(cannot_iter)


# In[15]:


from cogent3.util.misc import is_char

class foo:
    pass

is_char("a")


# In[16]:


is_char("ab")


# In[17]:


is_char(foo())


# In[18]:


from cogent3.util.misc import recursive_flatten

l = [[[[1, 2], "abcde"], [5, 6]], [7, 8], [9, 10]]


# In[19]:


recursive_flatten(l)


# In[20]:


from cogent3.util.misc import not_list_tuple

not_list_tuple(1)


# In[21]:


not_list_tuple([1])


# In[22]:


not_list_tuple("ab")


# In[23]:


from cogent3.util.misc import add_lowercase

d = {"A": 5, "B": 6, "C": 7, "foo": 8, 42: "life"}
add_lowercase(d)


# In[24]:


from cogent3.util.misc import DistanceFromMatrix
from numpy import array

m = array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
f = DistanceFromMatrix(m)
f(0, 0)


# In[25]:


f(1, 2)


# In[26]:


from cogent3.util.misc import ClassChecker

class not_okay(object):
    pass

no = not_okay()

class okay(object):
    pass

o = okay()

class my_dict(dict):
    pass

md = my_dict()
cc = ClassChecker(str, okay, dict)
o in cc


# In[27]:


no in cc


# In[28]:


5 in cc


# In[29]:


{"a": 5} in cc


# In[30]:


"asasas" in cc


# In[31]:


md in cc


# In[32]:


from cogent3.util.misc import Delegator

class ListAndString(list, Delegator):
    def __init__(self, items, string):
        Delegator.__init__(self, string)
        for i in items:
            self.append(i)

ls = ListAndString([1, 2, 3], "ab_cd")
len(ls)


# In[33]:


ls[0]


# In[34]:


ls.upper()


# In[35]:


ls.split("_")


# In[36]:


from cogent3.util.misc import FunctionWrapper

f = FunctionWrapper(str)
f


# In[37]:


f(123)


# In[38]:


from cogent3.util.misc import ConstrainedDict

d = ConstrainedDict({"a": 1, "b": 2, "c": 3}, constraint="abc")
d


# In[39]:


d["d"] = 5

