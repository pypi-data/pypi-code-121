import numpy as np

def normalize_vec(vec):
    """Normalizes a vector to a unit vector

        :param vec: Vector to normalize (Nx1 or 1xN)
        :type vec: numpy.ndarray
        :return: Normalized vector (Nx1 or 1xN)
        :rtype: numpy.ndarray
    """
    return vec / np.linalg.norm(vec)

def normalize_a_to_b(a, b):
    """Normalizes a vector from a to b

        :param a: Start position vector
        :type a: numpy.ndarray
        :param b: End position vector
        :type b: numpy.ndarray
        :return: Normalized vector from a to b
        :rtype: numpy.ndarray
    """
    vec = b - a
    return vec / np.linalg.norm(vec)

def calc_angle_360(v1, v2, n):
    """Calculates the angle within 360 degrees between two vectors :math:`v_1` and :math:`v_2` around normal :math:`n`.

        .. math::
        
            \\vec{x} &= \\vec{v_1} \\cdot \\vec{v_2} \\\\
            c &= sign(\\vec{x} \\cdot \\vec{n}) * |\\vec{x}| \\\\
            a &= \\tan^{-1} \\frac{c}{\\vec{v_1} \\cdot \\vec{v_2}}

        :param v1: Vector Nx1 or 1xN
        :type v1: numpy.ndarray
        :param v2: Vector Nx1 or 1xN
        :type v2: numpy.ndarray
        :param n: Vector Nx1 or 1xN
        :type n: numpy.ndarray
        :return: Angle in degrees
        :rtype: float
    """
    
    x = np.cross(v1, v2)
    c = np.sign(np.dot(x, n)) * np.linalg.norm(x)
    a = np.arctan2(c, np.dot(v1, v2))
    
    return np.degrees(a)