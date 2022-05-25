#!/usr/bin/env python3

import math
import numpy
from pyquats.quats import Quat
from pyquats.qtools import random_quat_Xwall
from pyquats.qtools import random_quat_Ywall
from pyquats.qtools import random_quat_Zwall

#unit_quat = Quat(1) # R_z(0)
#unit_quat = Quat.rot_quat([0, 0, 1], 0) # R_z(0)
#unit_quat = Quat.rot_quat([0, 0, 1], math.pi) # R_z(pi)
#unit_quat = Quat.rot_quat([0, 1, 0], math.pi) # R_y(pi)
#unit_quat = Quat.rot_quat([1, 0, 0], math.pi) # R_x(pi)
#unit_quat = Quat.rot_quat([0, 0, 1], math.pi * 0.5) # R_z(pi/2)
#unit_quat = Quat.rot_quat([0, 1, 0], math.pi * 0.5) # R_y(pi/2)
#unit_quat = Quat.rot_quat([1, 0, 0], math.pi * 0.5) # R_x(pi/2)
#unit_quat = Quat(0.5, 0.5, 0.5, 0.5)   # os [1,1,1], kat 120 stopni
#unit_quat = random_quat_Xwall()   # vector l || X
#unit_quat = random_quat_Ywall()   # vector l || Y
unit_quat = random_quat_Zwall()   # vector l || Z

q0, q1, q2, q3 = unit_quat.q

l_x = 2.0 * (q0 * q0 + q1 * q1) - 1.0
l_y = 2.0 * (q0 * q3 + q1 * q2)
l_z = 2.0 * (q1 * q3 - q0 * q2)
m_x = 2.0 * (q1 * q2 - q0 * q3)
m_y = 2.0 * (q0 * q0 + q2 * q2) - 1.0
m_z = 2.0 * (q0 * q1 + q2 * q3)
n_x = 2.0 * (q0 * q2 + q1 * q3)
n_y = 2.0 * (q2 * q3 - q0 * q1)
n_z = 2.0 * (q0 * q0 + q3 * q3) - 1.0

# Step to Legendre P2().
p2l_x = 1.5 * l_x * l_x - 0.5
p2l_y = 1.5 * l_y * l_y - 0.5
p2l_z = 1.5 * l_z * l_z - 0.5
p2m_x = 1.5 * m_x * m_x - 0.5
p2m_y = 1.5 * m_y * m_y - 0.5
p2m_z = 1.5 * m_z * m_z - 0.5
p2n_x = 1.5 * n_x * n_x - 0.5
p2n_y = 1.5 * n_y * n_y - 0.5
p2n_z = 1.5 * n_z * n_z - 0.5

# Special functions oriented along Z.
F200 = p2n_z
F202 = (p2l_z - p2m_z) / math.sqrt(3)
F220 = (p2n_x - p2n_y) / math.sqrt(3)
F222 = (p2l_x + p2m_y - p2m_x - p2l_y) / 3.0

print ( "unit_quat", repr(unit_quat) )
print ( "vector l", l_x, l_y, l_z )
print ( "vector m", m_x, m_y, m_z )
print ( "vector n", n_x, n_y, n_z )
print ( "F200", F200 )
print ( "F202", F202 )
print ( "F220", F220 )
print ( "F222", F222 )

# Wybieranie spinow w kolejnych iteracjach.
# Mozna zrobic kilka obiegow po wszystkich spinach.
x, y, z = 3, 4, 5
for it in range(2*x*y*z):
    i = (it // (z*y)) % x
    j = (it % (z*y)) // z
    k = (it % (z*y)) % z
    #print (i, j, k)

# EOF
