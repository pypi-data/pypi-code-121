#!/usr/bin/env python3

import random
import functools
import timeit
from pyquats.quats import Quat
#from pyquats.numpyquats import Quat

N = 1000000

a = [Quat(i) for i in range(1, N+1)]

b = [Quat(random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1),
    random.uniform(-1,1)).normalized() for i in range(N)]

print(sum(b))

print ( "Testing Quat (sum)..." )
t1 = timeit.Timer(lambda: sum(b))
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

print ( "Testing Quat (sum+reduce)..." )
t1 = timeit.Timer(lambda: functools.reduce(lambda x,y: x+y, b, Quat(0)))
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

print ( "Testing Quat (invert)..." )
t1 = timeit.Timer(lambda: [~q for q in b])
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

print ( "Testing Quat (conjugate)..." )
t1 = timeit.Timer(lambda: [q.conjugate() for q in b])
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

print ( "Testing Quat (neg)..." )
t1 = timeit.Timer(lambda: [-q for q in b])
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

print(functools.reduce(lambda x,y: x-y, b, Quat(0)))

print ( "Testing Quat (neg+reduce)..." )
t1 = timeit.Timer(lambda: functools.reduce(lambda x,y: x-y, b, Quat(0)))
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

print(functools.reduce(lambda x,y: x*y, b, Quat(1)))

print ( "Testing Quat (mul+reduce)..." )
t1 = timeit.Timer(lambda: functools.reduce(lambda x,y: x*y, b, Quat(1)))
print ( "{} {}".format(N, t1.timeit(1)) )   # single run

# EOF
