#!/usr/bin/env python3

import math
import random
from pyquats.quats import Quat
#from pyquats.numpyquats import Quat

# Rotates a vector with respect to a quat.
# The vector is from R^3, the result is from R^3, rot_quat is a unit quat.
def rotate1(vector, unit_quat):
    """Return the rotated vector (rot_quat used)."""
    # From a vector to a quaternion.
    vec_quat = Quat(0, vector[0], vector[1], vector[2])
    # Rotate a vector.
    vec_quat = unit_quat * vec_quat * (~unit_quat)
    # Return a vector from R^3.
    return vec_quat.q[1:]

# Rotates a vector angle 'radians' with respect to axis,
# both are vectors but it uses quaternions.
def rotate2(vector, axis, angle):
    """Return the rotated vector (axis and angle used)."""
    # Make a unit quat.
    unit_quat = Quat.rot_quat(axis, angle)
    return rotate1(vector, unit_quat)

def rotate3(vector, phi, theta, psi):
    """Return the rotated vector (Euler angles used)."""
    unit_quat = Quat.from_eulers(phi, theta, psi)
    return rotate1(vector, unit_quat)

def random_quat_uniax():
    """Return a random rotation quat for uniaxial molecules."""
    phi = random.uniform(0, 2*math.pi)
    ct = random.uniform(-1, 1)
    theta = math.acos(ct)   # mozna tez -ct
    quat = Quat.from_eulers(phi, theta, 0)
    return quat

def random_quat_biax():
    """Return a random rotation quat for biaxial molecules."""
    phi = random.uniform(0, 2*math.pi)
    ct = random.uniform(-1, 1)
    theta = math.acos(ct)   # mozna tez -ct
    psi = random.uniform(0, 2*math.pi)
    quat = Quat.from_eulers(phi, theta, psi)
    return quat

def random_quat_Xwall():
    """Return a random rotation quat for biaxial molecules at a X wall."""
    alpha = random.uniform(0, 2*math.pi)
    beta = random.choice((0, math.pi))
    #print("beta {}".format(beta))
    quat = Quat.from_x_rotation(alpha)
    quat *= Quat.from_z_rotation(beta)
    return quat

def random_quat_Ywall():
    """Return a random rotation quat for biaxial molecules at a Y wall."""
    alpha = random.uniform(0, 2*math.pi)
    beta = math.pi * random.choice((0.5, 1.5))
    #print("beta {}".format(beta))
    quat = Quat.from_y_rotation(alpha)
    quat *= Quat.from_z_rotation(beta)
    return quat

def random_quat_Zwall():
    """Return a random rotation quat for biaxial molecules at a Z wall."""
    alpha = random.uniform(0, 2*math.pi)
    beta = math.pi * random.choice((0.5, 1.5))
    #print("beta {}".format(beta))
    quat = Quat.from_z_rotation(alpha)
    quat *= Quat.from_y_rotation(beta)
    return quat

def random_pair():
    """Return a random pair (s1, s2), where s1^2 + s2^2 < 1."""
    while True:
        s1 = random.uniform(-1, 1)
        s2 = random.uniform(-1, 1)
        if s1 * s1 + s2 * s2 < 1:
            break
    return s1, s2

def random_unit_quat():
    """Return a random unit quat (Marsaglia, 1972)."""
    s1, s2 = random_pair()
    s3, s4 = random_pair()
    S1 = s1 * s1 + s2 * s2
    S2 = s3 * s3 + s4 * s4
    a = math.sqrt((1.0 - S1) / S2)
    return Quat(s1, s2, s3 * a, s4 * a)

def random_move_quat(ksi=1.0):
    """Return a Monte Carlo move (Barker, Watts, 1969)."""
    assert 0.0 <= ksi <= 1.0
    s1, s2 = random_pair()
    S = s1 * s1 + s2 * s2
    q1 = 2 * s1 * math.sqrt(1-S)
    q2 = 2 * s2 * math.sqrt(1-S)
    q3 = 1 - 2 * S
    # [q1, q2, q3] is now a unit vector.
    angle = random.uniform(-1, 1) * math.pi * 0.5 * 0.5 * ksi
    # math.pi * 0.5 gives all rotations,
    # 0.5 is for quat cos(angle/2), sin(angle/2).
    q0 = math.cos(angle)
    sinus = math.sin(angle)
    q1 *= sinus
    q2 *= sinus
    q3 *= sinus
    return Quat(q0, q1, q2, q3)

def random_move_Xwall(ksi=1.0):
    """Return a Monte Carlo move at a X wall."""
    # For biaxial molecules ksi=0.5 gives the same as ksi=1.0.
    # ksi=0.25 is better for low temperatures.
    alpha = random.uniform(-1, 1) * math.pi * ksi
    quat = Quat.from_x_rotation(alpha)
    return quat

def random_move_Ywall(ksi=1.0):
    """Return a Monte Carlo move at a Y wall."""
    # For biaxial molecules ksi=0.5 gives the same as ksi=1.0.
    # ksi=0.25 is better for low temperatures.
    alpha = random.uniform(-1, 1) * math.pi * ksi
    quat = Quat.from_y_rotation(alpha)
    return quat

def random_move_Zwall(ksi=1.0):
    """Return a Monte Carlo move at a Z wall."""
    # For biaxial molecules ksi=0.5 gives the same as ksi=1.0.
    # ksi=0.25 is better for low temperatures.
    alpha = random.uniform(-1, 1) * math.pi * ksi
    quat = Quat.from_z_rotation(alpha)
    return quat

# EOF
