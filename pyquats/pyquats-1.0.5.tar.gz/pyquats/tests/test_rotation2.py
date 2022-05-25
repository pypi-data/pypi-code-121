#!/usr/bin/env python3

import math
import numpy
from pyquats.quats import Quat

unit_quat = Quat(1) # R_z(0)
#unit_quat = Quat.from_z_rotation(0) # R_z(0)
#unit_quat = Quat.from_z_rotation(math.pi) # R_z(pi)
#unit_quat = Quat.from_y_rotation(math.pi) # R_y(pi)
#unit_quat = Quat.from_x_rotation(math.pi) # R_x(pi)
#unit_quat = Quat.from_z_rotation(math.pi * 0.5) # R_z(pi/2)
#unit_quat = Quat.from_y_rotation(math.pi * 0.5) # R_y(pi/2)
#unit_quat = Quat.from_x_rotation(math.pi * 0.5) # R_x(pi/2)
#unit_quat = Quat(0.5, 0.5, 0.5, 0.5)   # os [1,1,1], kat 120 stopni
#unit_quat = Quat.from_z_rotation(math.pi * 0.25) # R_z(pi/4)
#unit_quat = Quat.from_z_rotation(math.pi / 6.) # R_z(pi/6)

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

# Konfiguracja idealna R_z(0).
Qll_ideal = numpy.array([[1, 0, 0], [0, -0.5, 0], [0, 0, -0.5]], dtype=float)
Qmm_ideal = numpy.array([[-0.5, 0, 0], [0, 1, 0], [0, 0, -0.5]], dtype=float)
Qnn_ideal = numpy.array([[-0.5, 0, 0], [0, -0.5, 0], [0, 0, 1]], dtype=float)

# for R_z(pi/4)
# Do tensorow idealnych dodaje tensory obrocone R_z(pi/4)
# i wynik dziele przez 2.
#Qll = numpy.array([[5./8., 3./8., 0], [3./8., -1./8., 0], [0, 0, -0.5]], dtype=float)
#Qmm = numpy.array([[-1/8., -3/8., 0], [-3/8., 5/8., 0], [0, 0, -0.5]], dtype=float)
#Qnn = numpy.array([[-0.5, 0, 0], [0, -0.5, 0], [0, 0, 1]], dtype=float)

# for R_z(pi/6)
# Do tensorow idealnych dodaje tensory obrocone R_z(pi/6)
# i wynik dziele przez 2.
a = 3*math.sqrt(3)/16.
Qll = numpy.array([[13./16., a, 0], [a, -5./16., 0], [0, 0, -0.5]], dtype=float)
Qmm = numpy.array([[-5/16., -a, 0], [-a, 13/16., 0], [0, 0, -0.5]], dtype=float)
Qnn = numpy.array([[-0.5, 0, 0], [0, -0.5, 0], [0, 0, 1]], dtype=float)

print ( "Qll", Qll )
print ( "Qmm", Qmm )
print ( "Qnn", Qnn )

print ( "eigenvalues ll", numpy.linalg.eigvals(Qll) )
print ( "eigenvalues mm", numpy.linalg.eigvals(Qmm) )
print ( "eigenvalues nn", numpy.linalg.eigvals(Qnn) )

print ( "eig ll", numpy.linalg.eig(Qll) )
print ( "eig mm", numpy.linalg.eig(Qmm) )
print ( "eig nn", numpy.linalg.eig(Qnn) )

# EOF
