#!/usr/bin/env python3
#
# Based on Vesely (1982).
#
# Conclusions
# random_unit_quat() is 5 times faster that random_quat_biax(),
# but it is unclear if the distributions are similar.

import math
import random
import timeit
from pyquats.quats import Quat
from pyquats.qtools import random_quat_biax
from pyquats.qtools import random_unit_quat
from pyquats.qtools import random_move_quat
from pyquats.qtools import random_move_Xwall
from pyquats.qtools import random_move_Ywall
from pyquats.qtools import random_move_Zwall

for i in range(5):
    #q = random_unit_quat()
    #q = random_move_quat(0.5)
    q = random_move_Zwall(0.5)
    print(q)
    print(q.is_unit())
    print("abs {}".format(abs(q)))

N = 10000

print ( "random_quat_biax()..." )
t1 = timeit.Timer(lambda: random_quat_biax())
print ( "{} {}".format(N, t1.timeit(N)) )

print ( "random_unit_quat()..." )   # over 5 times faster
t1 = timeit.Timer(lambda: random_unit_quat())
print ( "{} {}".format(N, t1.timeit(N)) )

print ( "random_move_quat()..." )   # over 5 times faster
t1 = timeit.Timer(lambda: random_move_quat())
print ( "{} {}".format(N, t1.timeit(N)) )

print ( "random_move_Zwall()..." )   # over 5 times faster
t1 = timeit.Timer(lambda: random_move_Zwall(0.25))
print ( "{} {}".format(N, t1.timeit(N)) )

# EOF
