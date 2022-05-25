#!/usr/bin/env python3

import math
import numpy
from pyquats.quats import Quat
from pyquats.qtools import random_move_quat
from pyquats.qtools import random_move_Xwall
from pyquats.qtools import random_move_Ywall
from pyquats.qtools import random_move_Zwall

#unit_quat = Quat.from_x_rotation(math.pi)
#unit_quat = Quat.from_y_rotation(math.pi / 2.)
#unit_quat = Quat.from_x_rotation(math.pi * 0.5) * Quat.from_y_rotation(math.pi * 0.5) # n||x, l||y
#unit_quat = Quat.from_y_rotation(math.pi * 0.5) * Quat.from_x_rotation(math.pi * 0.5) # n||-y, l||-z
#unit_quat = Quat.from_z_rotation(math.pi / 2.)
#unit_quat = Quat.from_z_rotation(math.pi / 6.)
#unit_quat = Quat.from_z_rotation(math.pi / 6.) * Quat.from_y_rotation(math.pi / 2.)
#unit_quat = Quat.from_z_rotation(math.pi / 4.) * Quat.from_y_rotation(math.pi / 2.)
#unit_quat = random_move_quat(0.5)
unit_quat = random_move_Zwall(0.5)

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

print ( "unit_quat", repr(unit_quat) )
print ( "vector l", l_x, l_y, l_z )
print ( "vector m", m_x, m_y, m_z )
print ( "vector n", n_x, n_y, n_z )

# Sprawdzam dzialania na macierzach.
Qll = numpy.zeros((3,3), dtype=float)
Qmm = numpy.zeros((3,3), dtype=float)
Qnn = numpy.zeros((3,3), dtype=float)

Qll[0, 0] += 1.5 * l_x * l_x - 0.5
Qll[0, 1] += 1.5 * l_x * l_y
Qll[0, 2] += 1.5 * l_x * l_z
Qll[1, 1] += 1.5 * l_y * l_y - 0.5
Qll[1, 2] += 1.5 * l_y * l_z
Qll[2, 2] += 1.5 * l_z * l_z - 0.5
Qll[1, 0] = Qll[0, 1]
Qll[2, 0] = Qll[0, 2]
Qll[2, 1] = Qll[1, 2]

Qmm[0, 0] += 1.5 * m_x * m_x - 0.5
Qmm[0, 1] += 1.5 * m_x * m_y
Qmm[0, 2] += 1.5 * m_x * m_z
Qmm[1, 1] += 1.5 * m_y * m_y - 0.5
Qmm[1, 2] += 1.5 * m_y * m_z
Qmm[2, 2] += 1.5 * m_z * m_z - 0.5
Qmm[1, 0] = Qmm[0, 1]
Qmm[2, 0] = Qmm[0, 2]
Qmm[2, 1] = Qmm[1, 2]

Qnn[0, 0] += 1.5 * n_x * n_x - 0.5
Qnn[0, 1] += 1.5 * n_x * n_y
Qnn[0, 2] += 1.5 * n_x * n_z
Qnn[1, 1] += 1.5 * n_y * n_y - 0.5
Qnn[1, 2] += 1.5 * n_y * n_z
Qnn[2, 2] += 1.5 * n_z * n_z - 0.5
Qnn[1, 0] = Qnn[0, 1]
Qnn[2, 0] = Qnn[0, 2]
Qnn[2, 1] = Qnn[1, 2]

print ( "Qll", Qll )
print ( "Qmm", Qmm )
print ( "Qnn", Qnn )

print ( "Manual settings for Q" )

# Konfiguracja idealna na scianie prostopadlej do Z.
Qll_ideal = numpy.array([[-0.5, 0, 0], [0, -0.5, 0], [0, 0, 1]], dtype=float)
Qmm_ideal = numpy.array([[-0.5, 0, 0], [0, 1, 0], [0, 0, -0.5]], dtype=float)
Qnn_ideal = numpy.array([[1, 0, 0], [0, -0.5, 0], [0, 0, -0.5]], dtype=float)

print ( "Qll_ideal", Qll_ideal )
print ( "Qmm_ideal", Qmm_ideal )
print ( "Qnn_ideal", Qnn_ideal )

Qll = (Qll + Qll_ideal) / 2.
Qmm = (Qmm + Qmm_ideal) / 2.
Qnn = (Qnn + Qnn_ideal) / 2.

print ( "Qll", Qll )
print ( "Qmm", Qmm )
print ( "Qnn", Qnn )

# Wektory wlasne beda ulozone kolumnami!
# The column vec[:,i] is the eigenvector corresponding to the eigenvalue w[i].
w, vec =  numpy.linalg.eig(Qnn)
#print (w, vec)
print ("eigenvalues", w)
print ("unit eigenvectors (in columns)")
print (vec)

print ( "Diagonalizacja B^T Qll B ..." )
print ( numpy.dot(numpy.transpose(vec), numpy.dot(Qll,vec)) )
print ( "Diagonalizacja B^T Qmm B ..." )
print ( numpy.dot(numpy.transpose(vec), numpy.dot(Qmm,vec)) )
print ( "Diagonalizacja B^T Qnn B ..." )
print ( numpy.dot(numpy.transpose(vec), numpy.dot(Qnn,vec)) )

# EOF
