#!/usr/bin/env python3

try:
    real_types = (int, long, float)
    range = xrange
except NameError:   # Python 3
    real_types = (int, float)

import math
import random


class Quat:
    """The class defining a quaternion."""

    def __init__(self, x=0, y=0, z=0, t=0):
        """Create a Quat instance."""
        self.q = [float(x), float(y), float(z), float(t)]

    def __repr__(self):
        """Compute the string (formal) representation of the quaternion."""
        return "Quat({}, {}, {}, {})".format(*self.q)

    def __getitem__(self, key):
        """Implement quat[key]."""
        return self.q[key]

    def _normalize(self, other):
        """Transformation of an object to a quaternion."""
        if isinstance(other, real_types):
            other = Quat(other)
        elif isinstance(other, complex):
            other = Quat(other.real, other.imag)
        return other

    def __eq__(self, other):
        """Test if the quaternions are equal."""
        other = self._normalize(other)
        return self.q == other.q

    def __ne__(self, other):
        """Test if the quaternions are not equal."""
        return not self == other

    def __nonzero__(self):
        """Test if the quaternion is not equal to zero."""
        return self.q != [0.0, 0.0, 0.0, 0.0]

    __bool__ = __nonzero__   # Python 3

    def __pos__(self):
        """Implementation of +q."""
        return self

    def __neg__(self):
        """Implementation of -q."""
        return Quat(-self.q[0], -self.q[1], -self.q[2], -self.q[3])

    def __add__(self, other):
        """Addition of quaternions."""
        other = self._normalize(other)
        return Quat(self.q[0] + other.q[0], self.q[1] + other.q[1],
            self.q[2] + other.q[2], self.q[3] + other.q[3])

    __radd__ = __add__

    def __sub__(self, other):
        """Subtraction of quaternions."""
        # return self + (-other)
        other = self._normalize(other)
        return Quat(self.q[0] - other.q[0], self.q[1] - other.q[1],
            self.q[2] - other.q[2], self.q[3] - other.q[3])

    def __rsub__(self, other):
        """Subtraction of quaternions."""
        # return (-self) + other
        other = self._normalize(other)
        return Quat(other.q[0] - self.q[0], other.q[1] - self.q[1],
            other.q[2] - self.q[2], other.q[3] - self.q[3])

    def __mul__(self, other):
        """Quaternion product."""
        other = self._normalize(other)
        a = (self.q[0] * other.q[0] - self.q[1] * other.q[1]
            - self.q[2] * other.q[2] - self.q[3] * other.q[3])
        b = (self.q[0] * other.q[1] + self.q[1] * other.q[0]
            + self.q[2] * other.q[3] - self.q[3] * other.q[2])
        c = (self.q[0] * other.q[2] - self.q[1] * other.q[3]
            + self.q[2] * other.q[0] + self.q[3] * other.q[1])
        d = (self.q[0] * other.q[3] + self.q[1] * other.q[2]
            - self.q[2] * other.q[1] + self.q[3] * other.q[0])
        return Quat(a, b, c, d)

    def __rmul__(self, other):
        """Quaternion product."""
        other = self._normalize(other)
        a = (other.q[0] * self.q[0] - other.q[1] * self.q[1]
            - other.q[2] * self.q[2] - other.q[3] * self.q[3])
        b = (other.q[0] * self.q[1] + other.q[1] * self.q[0]
            + other.q[2] * self.q[3] - other.q[3] * self.q[2])
        c = (other.q[0] * self.q[2] - other.q[1] * self.q[3]
            + other.q[2] * self.q[0] + other.q[3] * self.q[1])
        d = (other.q[0] * self.q[3] + other.q[1] * self.q[2]
            - other.q[2] * self.q[1] + other.q[3] * self.q[0])
        return Quat(a, b, c, d)

    def __abs__(self):
        """Return the norm of a quaternion (a scalar)."""
        powers = sum(item * item for item in self.q)
        return math.sqrt(powers)

    norm = __abs__

    def norm_squared(self):
        """Return the squared norm of a quaternion (a scalar)."""
        return sum(item * item for item in self.q)

    def normalized(self):
        """Return a normalized version of this quaternion."""
        a = abs(self)
        return Quat(self.q[0] / a, self.q[1] / a, self.q[2] / a, self.q[3] / a)

    def is_unit(self):
        """Test a unit quaternion."""
        return 1.0 == sum(item * item for item in self.q)

    def conjugate(self):
        """Conjugate the quaternion."""
        return Quat(self.q[0], -self.q[1], -self.q[2], -self.q[3])

    def __invert__(self):   # ~p, return p^{-1}
        """Reciprocal of the quaternion."""
        powers = sum(item * item for item in self.q)
        return (1.0 / powers) * self.conjugate()

    def _pow1(self, n):
        """Find powers of the quaternion (inefficient)."""
        if n < 0:
            return pow(~self, -n)
        quat = Quat(1)
        while n > 0:
            quat = quat * self
            n = n - 1
        return quat

    def _pow2(self, n):
        """Find powers of the quaternion (binary exponentiation)."""
        if n == 0:
            return Quat(1)
        if n < 0:
            return pow(~self, -n)
        quat = self
        if n == 1:
            return self
        elif n == 2:
            return self * self
        else:   # binary exponentiation
            result = Quat(1)
            while True:
                if n % 2 == 1:
                    result = result * quat
                    n = n - 1  # przez ile pomnozyc
                    if n == 0:
                        break
                if n % 2 == 0:
                    quat = quat * quat
                    n = n // 2
        return result

    __pow__ = _pow2

    def __hash__(self):
        """Hashable quaternions."""
        return hash(tuple(self.q))

    def __int__(self):
        """Conversion to int is not possible."""
        raise TypeError("can't convert quat to int")

    def __long__(self):
        """Conversion to long is not possible."""
        raise TypeError("can't convert quat to long")

    def __float__(self):
        """Conversion to float is not possible."""
        raise TypeError("can't convert quat to float")

    def __complex__(self):
        """Conversion to complex is not possible."""
        raise TypeError("can't convert quat to complex")

    def apply_to_vector(self, vector):
        """Return the rotated vector."""
        if self.is_unit():
            unit_quat = self
        else:
            print("not a unit quaternion")
            unit_quat = self.normalized()
        if len(vector) != 3:
            raise ValueError("not a 3D vector")
        vec_quat = Quat(0, vector[0], vector[1], vector[2])
        vec_quat = unit_quat * vec_quat * (~unit_quat)
        # zwracamy wektor z R^3 (wycinek)
        return vec_quat.q[1:]   # list or numpy.array

    def get_rotation_matrix(self):
        """Return the rotation matrix."""
        w, x, y, z = self.q

        w2 = w * w
        x2 = x * x
        y2 = y * y
        z2 = z * z
        xy = x * y
        wz = w * z
        xz = x * z
        wy = w * y
        yz = y * z
        wx = w * x

        inverse = 1.0 / (w2 + x2 + y2 + z2)
        inverse2 = 2.0 * inverse

        m00 = (w2 + x2 - y2 - z2) * inverse
        m01 = (xy - wz) * inverse2
        m02 = (xz + wy) * inverse2

        m10 = (xy + wz) * inverse2
        m11 = (w2 - x2 + y2 - z2) * inverse
        m12 = (yz - wx) * inverse2

        m20 = (xz - wy) * inverse2
        m21 = (yz + wx) * inverse2
        m22 = (w2 - x2 - y2 + z2) * inverse

        return [[m00, m01, m02, 0.],
                [m10, m11, m12, 0.],
                [m20, m21, m22, 0.],
                [0., 0., 0., 1.]]

    # method used to create a rotation Quaternion to rotate
    # any vector defined as a Quaternion
    # with respect to the vector vect theta 'radians';
    # rot_vec ma dlugosc 1 w R^3, tworzymy kwaternion jednostkowy.
    # Chyba lepiej zrobic metode klasy.
    @classmethod
    def rot_quat(cls, axis, angle):
        """From the axis-angle representation to the quat.
        The angle is in radians. The axis is a unit 3D vector."""
        if len(axis) != 3:
            raise ValueError("not a 3D vector")
        length = math.sqrt(sum(x * x for x in axis))
        if length != 1.0:
            print("not a unit vector")
            axis = [x / length for x in axis]
        q0 = math.cos(angle / 2.0)
        sinus = math.sin(angle / 2.0)
        q1 = axis[0] * sinus
        q2 = axis[1] * sinus
        q3 = axis[2] * sinus
        return cls(q0, q1, q2, q3)

    @classmethod
    def from_x_rotation(cls, angle):
        """Create the unit quat for the X rotation."""
        return cls.rot_quat([1, 0, 0], angle)

    @classmethod
    def from_y_rotation(cls, angle):
        """Create the unit quat for the Y rotation."""
        return cls.rot_quat([0, 1, 0], angle)

    @classmethod
    def from_z_rotation(cls, angle):
        """Create the unit quat for the Z rotation."""
        return cls.rot_quat([0, 0, 1], angle)

    create_from_axis_rotation = rot_quat
    create_from_x_rotation = from_x_rotation
    create_from_y_rotation = from_y_rotation
    create_from_z_rotation = from_z_rotation

    @classmethod
    def from_eulers(cls, phi, theta, psi):
        """Create the unit quat from Euler angles."""
        unit_quat = cls.from_z_rotation(phi)
        unit_quat *= cls.from_y_rotation(theta)
        unit_quat *= cls.from_z_rotation(psi)
        return unit_quat

    @classmethod
    def random_quat_uniax(cls):
        """Return a random rotation quat for uniaxial molecules."""
        phi = random.uniform(0, 2*math.pi)
        ct = random.uniform(-1, 1)
        theta = math.acos(ct)   # mozna tez -ct
        quat = cls.from_eulers(phi, theta, 0)
        return quat

    @classmethod
    def random_quat_biax(cls):
        """Return a random rotation quat for biaxial molecules."""
        phi = random.uniform(0, 2*math.pi)
        ct = random.uniform(-1, 1)
        theta = math.acos(ct)   # mozna tez -ct
        psi = random.uniform(0, 2*math.pi)
        quat = cls.from_eulers(phi, theta, psi)
        return quat

    @staticmethod
    def random_pair():
        """Return a random pair (s1, s2), where s1^2 + s2^2 < 1."""
        while True:
            s1 = random.uniform(-1, 1)
            s2 = random.uniform(-1, 1)
            if s1 * s1 + s2 * s2 < 1:
                break
        return s1, s2

    @classmethod
    def random_unit_quat(cls):
        """Return a random unit quat (Marsaglia, 1972)."""
        s1, s2 = cls.random_pair()
        s3, s4 = cls.random_pair()
        S1 = s1 * s1 + s2 * s2
        S2 = s3 * s3 + s4 * s4
        a = math.sqrt((1.0 - S1) / S2)
        return cls(s1, s2, s3 * a, s4 * a)

    @classmethod
    def random_move_quat(cls, ksi=1.0):
        """Return a Monte Carlo move (Barker, Watts, 1969)."""
        assert 0.0 <= ksi <= 1.0
        s1, s2 = cls.random_pair()
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
        return cls(q0, q1, q2, q3)

Quaternion = Quat

# EOF
