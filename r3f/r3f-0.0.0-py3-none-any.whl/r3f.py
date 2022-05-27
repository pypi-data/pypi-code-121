"""
Copyright 2022 David Woodburn

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

--------------------------------------------------------------------------------
"""

__author__ = "David Woodburn"
__credits__ = ["John Raquet", "Mike Veth", "Alex McNeil"]
__license__ = "MIT"
__date__ = "2022-05-19"
__maintainer__ = "David Woodburn"
__email__ = "david.woodburn@icloud.com"
__status__ = "Development"

import numpy as np

# WGS84 constants (IS-GPS-200M and NIMA TR8350.2)
A_E = 6378137.0             # Earth's semi-major axis [m] (p. 109)
F_E = 298.257223563         # Earth's flattening constant (NIMA)


def is_square(C, N=3):
    """
    Check if the variable C is a square matrix with length N.

    Parameters
    ----------
    C : (N, N) np.ndarray
        Variable which should be a matrix.
    N : int, default 3
        Intended length of C matrix.

    Returns
    -------
    True if C is a square matrix of length N, False otherwise.
    """

    # Check the inputs.
    if not isinstance(N, int):
        raise Exception('is_square: N must be an integer.')

    if isinstance(C, np.ndarray) and (C.ndim == 2) and (C.shape == (N, N)):
        return True
    else:
        return False


def is_ortho(C):
    """
    Check if the matrix C is orthogonal.  It is assumed that C is a square
    2D np.ndarray (see is_square).

    Parameters
    ----------
    C : (N, N) np.ndarray
        Square matrix.

    Returns
    -------
    True if C is an orthogonal matrix, False otherwise.
    """

    N = len(C)
    Z = np.abs(C @ C.T - np.eye(N))
    check = np.sum(Z.flatten())
    return (check < N*N*1e-15)


def rpy_to_dcm(r, p, y):
    """
    Convert roll, pitch, and yaw angles to a direction cosine matrix that
    represents a zyx sequence of right-handed rotations.

    Parameters
    ----------
    r : float or int
        Roll in radians from -pi to pi.
    p : float or int
        Pitch in radians from -pi/2 to pi/2.
    y : float or int
        Yaw in radians from -pi to pi.

    Returns
    -------
    R : (3, 3) np.ndarray
        Rotation matrix.

    See Also
    --------
    dcm_to_rpy
    rot

    Notes
    -----
    This is equivalent to generating a rotation matrix for the rotation from the
    navigation frame to the body frame.  However, if you want to rotate from the
    body frame to the navigation frame (a xyz sequence of right-handed
    rotations), transpose the result of this function.  This is a convenience
    function.  You could instead use the `rot` function as follows::

        R = rot([yaw, pitch, roll], [2, 1, 0])

    However, the `rpy_to_dcm` function will compute faster than the `rot`
    function.
    """

    # Check inputs.
    if not isinstance(r, (float, int)) or not isinstance(p, (float, int)) \
            or not isinstance(y, (float, int)):
        raise Exception('rpy_to_dcm: r, p, and y must be floats or ints')
    if (abs(r) > np.pi) or (abs(p) > np.pi/2) or (abs(y) > np.pi):
        raise Exception('rpy_to_dcm: r and y must be bound by -pi and pi and ' +
                'p must be bound by -pi/2 and pi/2.')

    # Get the cosine and sine functions of the roll, pitch, and yaw.
    cr = np.cos(r)
    sr = np.sin(r)
    cp = np.cos(p)
    sp = np.sin(p)
    cy = np.cos(y)
    sy = np.sin(y)

    # Build and return the 3x3 matrix.
    R = np.array([
        [            cp*cy,             cp*sy,   -sp],
        [-cr*sy + sr*sp*cy,  cr*cy + sr*sp*sy, sr*cp],
        [ sr*sy + cr*sp*cy, -sr*cy + cr*sp*sy, cr*cp]])

    return R


def dcm_to_rpy(dcm):
    """
    Convert the direction cosine matrix, `dcm`, to vectors of `roll`, `pitch`,
    and `yaw` (in that order) Euler angles.

    This `dcm` represents the z-y-x sequence of right-handed rotations.  For
    example, if the DCM converted vectors from the navigation frame to the body
    frame, the roll, pitch, and yaw Euler angles would be the consecutive angles
    by which the vector would be rotated from the navigation frame to the body
    frame.  This is as opposed to the Euler angles required to rotate the vector
    from the body frame back to the navigation frame.

    Parameters
    ----------
    dcm : (3, 3) np.ndarray
        Rotation direction cosine matrix.

    Returns
    -------
    r : float
        Intrinsic rotation about the final reference frame's x axis.
    p : float
        Intrinsic rotation about the intermediate reference frame's y axis.
    y : float
        Intrinsic rotation about the initial reference frame's z axis.

    See Also
    --------
    rpy_to_dcm
    rot

    Notes
    -----
    If we define `dcm` as ::

              .-             -.
              |  d11 d12 d13  |
        dcm = |  d21 d22 d23  |
              |  d31 d32 d33  |
              '-             -'
              .-                                                 -.
              |       (cy cp)             (sy cp)          -sp    |
            = |  (cy sp sr - sy cr)  (sy sp sr + cy cr)  (cp sr)  |
              |  (sy sr + cy sp sr)  (sy sp cr - cy sr)  (cp cr)  |
              '-                                                 -'

    where `c` and `s` mean cosine and sine, respectively, and `r`, `p`, and `y`
    mean roll, pitch, and yaw, respectively, then we can see that ::

                                    .-       -.
                                    |  cp sr  |
        r = atan2(d23, d33) => atan | ------- |
                                    |  cp cr  |
                                    '-       -'
                                    .-       -.
                                    |  sy cp  |
        y = atan2(d12, d11) => atan | ------- |
                                    |  cy cp  |
                                    '-       -'

    where the cp values cancel in both cases.  The value for pitch could be
    found from d13 alone::

        p = asin(-d13)

    However, this tends to suffer from numerical error around +/- pi/2.  So,
    instead, we will use the fact that ::

          2     2               2     2
        cy  + sy  = 1   and   cr  + sr  = 1 .

    Therefore, we can use the fact that ::

           .------------------------
          /   2      2      2      2     .--
         V d11  + d12  + d23  + d33  =  V 2  cos( |p| )

    to solve for pitch.  We can use the negative of the sign of d13 to give the
    proper sign to pitch.  The advantage is that in using more values from the
    dcm matrix, we can can get a value which is more accurate.  This works well
    until we get close to a pitch value of zero.  Then, the simple formula for
    pitch is actually better.  So, we will use both and do a weighted average of
    the two, based on pitch.

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    """

    # Check inputs.
    if not is_square(dcm, 3):
        raise Exception('dcm_to_rpy: dcm must be a (3, 3) np.ndarray')
    if not is_ortho(dcm):
        raise Exception('dcm_to_rpy: dcm must be orthogonal')

    # Get roll and yaw.
    r = np.arctan2(dcm[1, 2], dcm[2, 2])
    y = np.arctan2(dcm[0, 1], dcm[0, 0])

    # Get pitch.
    sp = -dcm[0, 2]
    pa = np.arcsin(sp)
    n = np.sqrt(dcm[0, 0]**2 + dcm[0, 1]**2 + dcm[1, 2]**2 + dcm[2, 2]**2)
    pb = np.arccos(n/np.sqrt(2))
    p = (1.0 - abs(sp))*pa + sp*pb

    return r, p, y


def rpy_to_quat(r, p, y):
    """
    Convert roll, pitch, and yaw to a quaternion, `quat`, vector.  Both
    represent the same right-handed frame rotations.

    Parameters
    ----------
    r : float or int or (N,) np.ndarray
        Roll angles in radians.
    p : float or int or (N,) np.ndarray
        Pitch angles in radians.
    y : float or int or (N,) np.ndarray
        Yaw angles in radians.

    Returns
    -------
    quat : (4,) np.ndarray or (4, N) np.ndarray
        The quaternion vector or a matrix of such vectors.

    See Also
    --------
    quat_to_rpy

    Notes
    -----
    An example use case is to calculate a quaternion that rotates from the
    [nose, right wing, down] body frame to the [north, east, down] navigation
    frame when given a yaw-pitch-roll (z-y-x) frame rotation.

    This function makes sure that the first element of the quaternion is always
    positive.

    The equations to calculate the quaternion are ::

        h = cr cp cy + sr sp sy
        a = sgn(h) h
        b = sgn(h) (sr cp cy - cr sp sy)
        c = sgn(h) (cr sp cy + sr cp sy)
        d = sgn(h) (cr cp sy - sr sp cy)

    where the quaternion is [`a`, `b`, `c`, `d`], the `c` and `s` prefixes
    represent cosine and sine, respectively, the `r`, `p`, and `y` suffixes
    represent roll, pitch, and yaw, respectively, and `sgn` is the sign
    function.  The sign of `h` is used to make sure that the first element of
    the quaternion is always positive.  This is simply a matter of convention.

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    """

    # Depending on the types of inputs,
    if isinstance(r, (float, int)) and isinstance(p, (float, int)) and \
            isinstance(y, (float, int)):
        # Get the half-cosine and half-sines of roll, pitch, and yaw.
        cr = np.cos(r/2.0)
        cp = np.cos(p/2.0)
        cy = np.cos(y/2.0)
        sr = np.sin(r/2.0)
        sp = np.sin(p/2.0)
        sy = np.sin(y/2.0)

        # Build the quaternion vector.
        h = cr*cp*cy + sr*sp*sy
        sgn_h = np.sign(h)
        quat = np.array([sgn_h*h,
                sgn_h*(sr*cp*cy - cr*sp*sy),
                sgn_h*(cr*sp*cy + sr*cp*sy),
                sgn_h*(cr*cp*sy - sr*sp*cy)])
    elif isinstance(r, np.ndarray) and (r.ndim == 1) and \
            isinstance(p, np.ndarray) and (p.ndim == 1) and \
            isinstance(y, np.ndarray) and (y.ndim == 1) and \
            (len(r) == len(p)) and (len(p) == len(y)):
        # Get the half-cosine and half-sines of roll, pitch, and yaw.
        cr = np.cos(r/2.0)
        cp = np.cos(p/2.0)
        cy = np.cos(y/2.0)
        sr = np.sin(r/2.0)
        sp = np.sin(p/2.0)
        sy = np.sin(y/2.0)

        # Build the matrix of quaternion vectors.
        quat = np.zeros((4, len(r)))
        h = cr*cp*cy + sr*sp*sy
        sgn_h = np.sign(h)
        quat[0, :] = sgn_h*h
        quat[1, :] = sgn_h*(sr*cp*cy - cr*sp*sy)
        quat[2, :] = sgn_h*(cr*sp*cy + sr*cp*sy)
        quat[3, :] = sgn_h*(cr*cp*sy - sr*sp*cy)
    else:
        raise Exception('rpy_to_quat: r, p, and y must be floats or ' +
                '(N,) np.ndarrays of equal lengths')

    return quat


def quat_to_rpy(quat):
    """
    Convert from a quaternion right-handed frame rotation to a roll, pitch, and
    yaw, z-y-x sequence of right-handed frame rotations.  If frame 1 is rotated
    in a z-y-x sequence to become frame 2, then the quaternion `quat` would also
    rotate a vector in frame 1 into frame 2.

    Parameters
    ----------
    quat : (4,) np.ndarray or (4, N) np.ndarray
        A quaternion vector or a matrix of such vectors.

    Returns
    -------
    r : float or (N,) np.ndarray
        Roll angles in radians.
    p : float or (N,) np.ndarray
        Pitch angles in radians.
    y : float or (N,) np.ndarray
        Yaw angles in radians.

    See Also
    --------
    rpy_to_quat

    Notes
    -----
    An example use case is the calculation a yaw-roll-pitch (z-y-x) frame
    rotation when given the quaternion that rotates from the [nose, right wing,
    down] body frame to the [north, east, down] navigation frame.

    From the dcm_to_rpy function, we know that the roll, `r`, pitch, `p`, and
    yaw, `y`, can be calculated as follows::

        r = atan2(d23, d33)
        p = -asin(d13)
        y = atan2(d12, d11)

    where the `d` variables are elements of the DCM.  We also know from the
    quat_to_dcm function that ::

              .-                                                            -.
              |   2    2    2    2                                           |
              | (a  + b  - c  - d )    2 (b c + a d)       2 (b d - a c)     |
              |                                                              |
              |                       2    2    2    2                       |
        Dcm = |    2 (b c - a d)    (a  - b  + c  - d )    2 (c d + a b)     |
              |                                                              |
              |                                           2    2    2    2   |
              |    2 (b d + a c)       2 (c d - a b)    (a  - b  - c  + d )  |
              '-                                                            -'

    This means that the `d` variables can be defined in terms of the quaternion
    elements::

               2    2    2    2
        d11 = a  + b  - c  - d           d12 = 2 (b c + a d)

                                         d13 = 2 (b d - a c)
               2    2    2    2
        d33 = a  - b  - c  + d           d23 = 2 (c d + a b)

    This function does not take advantage of the more advanced formula for pitch
    because testing showed it did not help in this case.

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    """

    # Check inputs.
    if not isinstance(quat, np.ndarray) or (quat.ndim > 2):
        raise Exception('quat_to_rpy: quat must be an np.ndarray ' +
                'of less than 3 dimensions')

    # Depending on the dimensions of the input,
    if quat.ndim == 1:
        # Get the required elements of the DCM.
        d11 = quat[0]**2 + quat[1]**2 - quat[2]**2 - quat[3]**2
        d12 = 2*(quat[1]*quat[2] + quat[0]*quat[3])
        d13 = 2*(quat[1]*quat[3] - quat[0]*quat[2])
        d23 = 2*(quat[2]*quat[3] + quat[0]*quat[1])
        d33 = quat[0]**2 - quat[1]**2 - quat[2]**2 + quat[3]**2

        # Build the output.
        rpy = np.zeros(3)
        rpy[0] = np.arctan2(d23, d33)
        rpy[1] = -np.arcsin(d13)
        rpy[2] = np.arctan2(d12, d11)
    else:
        # Get the required elements of the DCM.
        d11 = quat[0, :]**2 + quat[1, :]**2 - quat[2, :]**2 - quat[3, :]**2
        d12 = 2*(quat[1, :]*quat[2, :] + quat[0, :]*quat[3, :])
        d13 = 2*(quat[1, :]*quat[3, :] - quat[0, :]*quat[2, :])
        d23 = 2*(quat[2, :]*quat[3, :] + quat[0, :]*quat[1, :])
        d33 = quat[0, :]**2 - quat[1, :]**2 - quat[2, :]**2 + quat[3, :]**2

        # Build the output.
        rpy = np.zeros((3, quat.shape[1]))
        rpy[0, :] = np.arctan2(d23, d33)
        rpy[1, :] = -np.arcsin(d13)
        rpy[2, :] = np.arctan2(d12, d11)

    return rpy


def dcm_to_quat(dcm):
    """
    Convert a direction cosine matrix, `dcm`, to a quaternion vector, `quat`.
    Here, the `dcm` is considered to represent a z-y-x sequence of right-handed
    rotations.  This means it has the same sense as the quaternion.

    The implementation here is Cayley's method for obtaining the quaternion.  It
    is used because of its superior numerical accuracy.  This comes from the
    fact that it uses all nine of the elements of the DCM matrix.  It also does
    not suffer from numerical instability due to division as some other methods
    do.

    Parameters
    ----------
    dcm : (3, 3) np.ndarray
        Rotation direction cosine matrix.

    Returns
    -------
    quat : (4,) np.ndarray
        The quaternion vector.

    See Also
    --------
    quat_to_dcm

    Notes
    -----
    FIXME

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    .. [2]  Soheil Sarabandi and Federico Thomas, "A Survey on the Computation
            of Quaternions from Rotation Matrices"
    """

    # Ensure the input is a 3-by-3 np.ndarray.
    if not is_square(dcm, 3):
        raise Exception('dcm_to_quat: dcm must be a (3, 3) np.ndarray')
    if not is_ortho(dcm):
        raise Exception('dcm_to_quat: dcm must be orthogonal')

    # Parse the elements of dcm.
    d00 = dcm[0, 0]
    d01 = dcm[0, 1]
    d02 = dcm[0, 2]
    d10 = dcm[1, 0]
    d11 = dcm[1, 1]
    d12 = dcm[1, 2]
    d20 = dcm[2, 0]
    d21 = dcm[2, 1]
    d22 = dcm[2, 2]

    # Get the squared sums and differences of off-diagonal pairs.
    p01 = (d01 + d10)**2
    p12 = (d12 + d21)**2
    p20 = (d20 + d02)**2
    m01 = (d01 - d10)**2
    m12 = (d12 - d21)**2
    m20 = (d20 - d02)**2

    # Get the magnitudes.
    n0 = np.sqrt((d00 + d11 + d22 + 1)**2 + m12 + m20 + m01)
    n1 = np.sqrt(m12 + (d00 - d11 - d22 + 1)**2 + p01 + p20)
    n2 = np.sqrt(m20 + p01 + (d11 - d00 - d22 + 1)**2 + p12)
    n3 = np.sqrt(m01 + p20 + p12 + (d22 - d00 - d11 + 1)**2)

    # Build the quaternion output.
    quat = 0.25*np.array([n0, np.sign(d12 - d21)*n1,
            np.sign(d20 - d02)*n2, np.sign(d01 - d10)*n3])

    return quat


def quat_to_dcm(quat):
    """
    Convert from a quaternion, `quat`, that performs a right-handed frame
    rotation from frame 1 to frame 2 to a direction cosine matrix, `dcm`, that
    also performs a right-handed frame rotation from frame 1 to frame 2.  The
    `dcm` represents a z-y-x sequence of right-handed rotations.

    Parameters
    ----------
    quat : 4-element 1D np.ndarray
        The 4-element quaternion vector corresponding to the DCM.

    Returns
    -------
    dcm : float 3x3 np.ndarray
        3-by-3 rotation direction cosine matrix.

    See Also
    --------
    dcm_to_quat

    Notes
    -----
    An example use case is to calculate a direction cosine matrix that rotates
    from the [nose, right wing, down] body frame to the [north, east, down]
    navigation frame when given a quaternion frame rotation that rotates from
    the [nose, right wing, down] body frame to the [north, east, down]
    navigation frame.

    The DCM can be defined in terms of the elements of the quaternion
    [a, b, c, d] as ::

              .-                                                            -.
              |   2    2    2    2                                           |
              | (a  + b  - c  - d )    2 (b c + a d)       2 (b d - a c)     |
              |                                                              |
              |                       2    2    2    2                       |
        dcm = |    2 (b c - a d)    (a  - b  + c  - d )    2 (c d + a b)     |
              |                                                              |
              |                                           2    2    2    2   |
              |    2 (b d + a c)       2 (c d - a b)    (a  - b  - c  + d )  |
              '-                                                            -'

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    """

    # Ensure the input is a 4-element np.ndarray.
    if not isinstance(quat, np.ndarray) or (quat.shape != (4,)):
        raise Exception('quat_to_dcm: quat must be a 4-element np.ndarray')

    # Square the elements of the quaternion.
    q0 = quat[0]*quat[0]
    q1 = quat[1]*quat[1]
    q2 = quat[2]*quat[2]
    q3 = quat[3]*quat[3]

    # Build the DCM.
    dcm = np.array([
        [q0 + q1 - q2 - q3,
            2*(quat[1]*quat[2] + quat[0]*quat[3]),
            2*(quat[1]*quat[3] - quat[0]*quat[2])],
        [2*(quat[1]*quat[2] - quat[0]*quat[3]),
            q0 - q1 + q2 - q3,
            2*(quat[2]*quat[3] + quat[0]*quat[1])],
        [2*(quat[1]*quat[3] + quat[0]*quat[2]),
            2*(quat[2]*quat[3] - quat[0]*quat[1]),
            q0 - q1 - q2 + q3]])

    return dcm


def rpy_to_axis_angle(r, p, y):
    """
    Convert roll, pitch, and yaw Euler angles to rotation axis vector and
    rotation angle.

    Parameters
    ----------
    r : float or (N,) np.ndarray
        Roll angles in radians.
    p : float or (N,) np.ndarray
        Pitch angles in radians.
    y : float or (N,) np.ndarray
        Yaw angles in radians.

    Returns
    -------
    ax : (3,) np.ndarray or (3, N) np.ndarray
        Axis vector or matrix of vectors.
    ang : float or (N,) np.ndarray
        Rotation angles in radians.

    See Also
    --------
    axis_angle_to_rpy

    Notes
    -----
    Both (r, p, y) and (ax, ang) represent the same z, y, x sequence of
    right-handed frame rotations.  The conversion happens through an
    intermediate step of calculating the quaternion.  This function makes sure
    that the first element of the quaternion is always positive.

    The equations to calculate the quaternion are ::

        h = cr cp cy + sr sp sy
        a = sgn(h) h
        b = sgn(h) (sr cp cy - cr sp sy)
        c = sgn(h) (cr sp cy + sr cp sy)
        d = sgn(h) (cr cp sy - sr sp cy)

    where the quaternion is `[a, b, c, d]`, the `c` and `s` prefixes
    represent cosine and sine, respectively, the `r`, `p`, and `y` suffixes
    represent roll, pitch, and yaw, respectively, and `sgn` is the sign
    function.  The sign of `h` is used to make sure that the first element of
    the quaternion is always positive.  This is simply a matter of convention.

    Defining the rotation axis vector to be a unit vector, we will define the
    quaterion, `quat`, in terms of the axis and angle:

                  .-     -.               .-     -.              .-   -.
                  |  ang  |               |  ang  |              |  x  |
          a = cos | ----- |     b = x sin | ----- |         ax = |  y  |
                  |   2   |               |   2   |              |  z  |
                  '-     -'               '-     -'              '-   -'
                  .-     -.               .-     -.              .-   -.
                  |  ang  |               |  ang  |              |  a  |
        c = y sin | ----- |     d = z sin | ----- |       quat = |  b  | ,
                  |   2   |               |   2   |              |  c  |
                  '-     -'               '-     -'              |  d  |
                                                                 '-   -'

    Then, the norm of `[b, c, d]` will be

          .-------------     .-----------------------------
         /  2    2    2     /  2    2    2     2 .- ang -.   |     .- ang -. |
        V  b  + c  + d  =  / (x  + y  + z ) sin  | ----- | = | sin | ----- | | .
                          V                      '-  2  -'   |     '-  2  -' |

    Since `a = cos(ang/2)`, with the above value we can get the angle by ::

                        .-  .------------   -.
                        |  /  2    2    2    |
        ang = 2 s atan2 | V  b  + c  + d , a | ,
                        '-                  -'

    where `s` is the sign of the angle determined based on whether the dot
    product of the vector `[b, c, d]` with `[1, 1, 1]` is positive:

        s = sign( b + c + d ) .

    Finally, the axis is calculated by using the first set of equations above:

                  b                     c                     d
        x = -------------     y = -------------     z = ------------- .
                .- ang -.             .- ang -.             .- ang -.
            sin | ----- |         sin | ----- |         sin | ----- |
                '-  2  -'             '-  2  -'             '-  2  -'

    It is true that `ang` and, therefore `sin(ang/2)`, could become 0, which
    would create a singularity.  But, this will happen only if the norm of `[b,
    c, d]` is zero.  In other words, if the quaternion is a vector with only one
    non-zero value, then we will have a problem.

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    """

    # Depending on the dimensions of the inputs,
    if isinstance(r, (float, int)) and isinstance(p, (float, int)) and \
            isinstance(y, (float, int)):
        # Get the cosines and sines of the half angles.
        cr = np.cos(r/2.0)
        sr = np.sin(r/2.0)
        cp = np.cos(p/2.0)
        sp = np.sin(p/2.0)
        cy = np.cos(y/2.0)
        sy = np.sin(y/2.0)

        # Build the quaternion.
        h = cr*cp*cy + sr*sp*sy
        sgn_h = np.sign(h)
        q1 = sgn_h*h
        q2 = sgn_h*(sr*cp*cy - cr*sp*sy)
        q3 = sgn_h*(cr*sp*cy + sr*cp*sy)
        q4 = sgn_h*(cr*cp*sy - sr*sp*cy)

        # Get the norm and sign of the last three elements of the quaternion.
        ax_norm = np.sqrt(q2**2 + q3**2 + q4**2)
        s = np.sign(q2 + q3 + q4)

        # Get the angle of rotation.
        ang = 2*s*np.arctan2(ax_norm, q1)

        # Build the rotation axis vector.
        ax = np.zeros(3)
        k = 1/np.sin(ang/2)
        ax[0] = q2*k
        ax[1] = q3*k
        ax[2] = q4*k

    elif isinstance(r, np.ndarray) and (r.ndim == 1) and \
            isinstance(p, np.ndarray) and (p.ndim == 1) and \
            isinstance(y, np.ndarray) and (y.ndim == 1) and \
            (len(r) == len(p)) and (len(p) == len(y)):
        # Get the cosines and sines of the half angles.
        cr = np.cos(r/2.0)
        sr = np.sin(r/2.0)
        cp = np.cos(p/2.0)
        sp = np.sin(p/2.0)
        cy = np.cos(y/2.0)
        sy = np.sin(y/2.0)

        # Build the quaternion.
        h = cr*cp*cy + sr*sp*sy
        sgn_h = np.sign(h)
        q1 = sgn_h*h
        q2 = sgn_h*(sr*cp*cy - cr*sp*sy)
        q3 = sgn_h*(cr*sp*cy + sr*cp*sy)
        q4 = sgn_h*(cr*cp*sy - sr*sp*cy)

        # Get the norm and sign of the last three elements of the quaternion.
        ax_norm = np.sqrt(q2**2 + q3**2 + q4**2)
        s = np.sign(q2 + q3 + q4)

        # Get the angle of rotation.
        ang = 2*s*np.arctan2(ax_norm, q1)

        # Build the rotation axis vector.
        ax = np.zeros((3, len(r)))
        k = 1/np.sin(ang/2)
        ax[0, :] = q2*k
        ax[1, :] = q3*k
        ax[2, :] = q4*k
    else:
        raise Exception('rpy_to_axis_angle: r, p, and y must be scalars or ' +
                '(N,) np.ndarrays of equal lengths.')

    return ax, ang


# FIXME add axis_angle_to_rpy
# FIXME add dcm_to_axis_angle
# FIXME add axis_angle_to_dcm
# FIXME add quat_to_axis_angle
# FIXME add axis_angle_to_quat


def axis_angle_to_dcm(ax, ang):
    """
    Create a direction cosine matrix (DCM) (also known as a rotation matrix) to
    rotate from one frame to another given a rotation `ax` vector and a
    right-handed `ang` of rotation.

    Parameters
    ----------
    ax : array_like
        Vector of the rotation axis with three values.
    ang : float
        Rotation ang in radians.

    Returns
    -------
    R : 2D np.ndarray
        3x3 rotation matrix.
    """

    # Normalize the rotation axis vector.
    ax = ax/np.norm(ax)

    # Parse the rotation axis vector into its three elements.
    x = ax[0]
    y = ax[1]
    z = ax[2]

    # Get the cosine and sine of the ang.
    co = np.cos(ang)
    si = np.sin(ang)

    # Build the direction cosine matrix.
    R = np.array([
        [ co + x**2*(1 - co), x*y*(1 - co) - z*si, x*z*(1 - co) + y*si],
        [y*x*(1 - co) + z*si,  co + y**2*(1 - co), y*z*(1 - co) - x*si],
        [z*x*(1 - co) - y*si, z*y*(1 - co) + x*si,  co + z**2*(1 - co)]])

    return R


def rot(ang, ax=2, degrees=False):
    """
    Build a three-dimensional rotation matrix of rotation angle `ang` about
    the axis `ax`.

    Parameters
    ----------
    ang : float or int or array_like
        Angle of rotation in radians (or degrees if `degrees` is True).
    ax : {0, 1, 2}, float or int or array_like, default 2
        Axis about which to rotate.
    degrees : bool, default False
        A flag denoting whether the values of `ang` are in degrees.

    See Also
    --------
    rpy_to_dcm

    Returns
    -------
    R : 2D np.ndarray
        3x3 rotation matrix
    """

    # Control the input types.
    if isinstance(ang, (float, int)):
        ang = np.array([float(ang)])
    elif isinstance(ang, list):
        ang = np.array(ang, dtype=float)
    if isinstance(ax, (float, int)):
        ax = np.array([int(ax)])
    elif isinstance(ax, list):
        ax = np.array(ax, dtype=int)

    # Check the lengths of ang and ax.
    if len(ang) != len(ax):
        raise Exception("rot: ang and ax must be the same length!")
    else:
        N = len(ang)

    # Convert degrees to radians.
    if degrees:
        ang *= DEG_TO_RAD

    # Build the rotation matrix.
    R = np.eye(3)
    for n in range(N):
        # Skip trivial rotations.
        if ang[n] == 0:
            continue

        # Get the cosine and sine of this ang.
        co = np.cos(ang[n])
        si = np.sin(ang[n])

        # Pre-multiply by another matrix.
        if ax[n] == 0:
            R = np.array([[1, 0, 0], [0, co, si], [0, -si, co]]).dot(R)
        elif ax[n] == 1:
            R = np.array([[co, 0, -si], [0, 1, 0], [si, 0, co]]).dot(R)
        elif ax[n] == 2:
            R = np.array([[co, si, 0], [-si, co, 0], [0, 0, 1]]).dot(R)
        else:
            raise Exception("rot: Axis must be 0 to 2.")

    return R


def ecef_to_geodetic(xe, ye, ze):
    """
    Convert an ECEF (Earth-centered, Earth-fixed) position to geodetic
    coordinates.  This follows the WGS-84 definitions (see WGS-84 Reference
    System (DMA report TR 8350.2)).

    Parameters
    ----------
    xe, ye, ze : float
        ECEF x, y, and z-axis position values in meters.

    Returns
    -------
    phi : float
        Geodetic latitude in radians.
    lam : float
        Geodetic longitude in radians.
    hae : float
        Height above ellipsoid in meters.

    See Also
    --------
    geodetic_to_ecef

    Notes
    -----
    Note that inherent in solving the problem of getting the geodetic latitude
    and ellipsoidal height is finding the roots of a quartic polynomial because
    we are looking for the intersection of a line with an ellipse.  While there
    are closed-form solutions to this problem (see Wikipedia), each point has
    potentially four solutions and the solutions are not numerically stable.
    Instead, this function uses the Newton-Raphson method to iteratively solve
    for the geodetic coordinates.

    First, we want to approximate the values for geodetic latitude, `phi`, and
    height above ellipsoid, `hae`, given the (x, y, z) position in the ECEF
    frame::

                                .------
                               / 2    2
        hae = 0         rho = V x  + y             phi = atan2(z, rho),

    where `rho` is the distance from the z axis of the ECEF frame.  (While there
    are better approximations for `hae` than zero, the improvement in accuracy
    was not enough to reduce the number of iterations and the additional
    computational burden could not be justified.)  Then, we will iteratively use
    this approximation for `phi` and `hae` to calculate what `rho` and `z` would
    be, get the residuals given the correct `rho` and `z` values in the ECEF
    frame, use the inverse Jacobian to calculate the corresponding residuals of
    `phi` and `hae`, and update our approximations for `phi` and `hae` with
    those residuals.  In testing millions of randomly generated points, three
    iterations was sufficient to reach the limit of numerical precision for
    64-bit floating-point numbers.

    So, first, let us define the transverse, `Rt`, and meridional, `Rm`, radii::

                                   .-        -.               .--------------
              a                a   |       2  |              /     2   2
        Rt = ----       Rm = ----- |  1 - e   |     kphi =  V 1 - e sin (phi) ,
             kphi                3 |          |
                             kphi  '-        -'

    where `e` is the eccentricity of the Earth, and `a` is the semi-major radius
    of the Earth.  The ECEF-frame `rho` and `z` values given the approximations
    to geodetic latitude, `phi`, and height above ellipsoid, `hae`, are ::

         ~                              ~                    2
        rho = cos(phi) (Rt + hae)       z = sin(phi) (Rm kphi + hae) .

    We already know the correct values for `rho` and `z`, so we can get
    residuals::

                      ~                         ~
        drho = rho - rho               dz = z - z .

    We can relate the `rho` and `z` residuals to the `phi` and `hae` residuals
    by using the inverse Jacobian matrix::

        .-    -.       .-    -.
        | dphi |    -1 | drho |
        |      | = J   |      | .
        | dhae |       |  dz  |
        '-    -'       '-    -'

    With a bit of algebra, we can combine and simplify the calculation of the
    Jacobian with the calculation of the `phi` and `hae` residuals::

        dhae = ( c*drho + s*dz)
        dphi = (-s*drho + c*dz)/(Rm + hae) .

    Conceptually, this is the backwards rotation of the (`drho`, `dz`) vector by
    the angle `phi`, where the resulting y component of the rotated vector is
    treated as an arc length and converted to an angle, `dphi`, using the radius
    `Rm` + `hae`.  With the residuals for `phi` and `hae`, we can update our
    approximations for `phi` and `hae`::

        phi = phi + dphi
        hae = hae + dhae

    and iterate again.  Finally, the longitude, `lam`, is exactly the arctangent
    of the ECEF `x` and `y` values::

        lam = atan2(y, x) .

    References
    ----------
    .. [1]  WGS-84 Reference System (DMA report TR 8350.2)
    .. [2]  Inertial Navigation: Theory and Implementation by David Woodburn and
            Robert Leishman
    """

    # Reform the inputs to ndarrays of floats.
    x = np.asarray(xe).astype(float)
    y = np.asarray(ye).astype(float)
    z = np.asarray(ze).astype(float)

    # Initialize the height above the ellipsoid.
    hae = 0

    # Get the true radial distance from the z axis.
    rho = np.sqrt(x**2 + y**2)

    # Initialize the estimated ground latitude.
    phi = np.arctan2(z, rho) # bound to [-pi/2, pi/2]

    # Iterate to reduce residuals of the estimated closest point on the ellipse.
    for _ in range(3):
        # Using the estimated ground latitude, get the cosine and sine.
        co = np.cos(phi)
        si = np.sin(phi)
        kphi2 = 1 - E2*si**2
        kphi = np.sqrt(kphi2)
        Rt = A_E/kphi
        Rm = A_E*(1 - E2)/(kphi*kphi2)

        # Get the estimated position in the meridional plane (the plane defined
        # by the longitude and the z axis).
        rho_est = co*(Rt + hae)
        z_est = si*(Rm*kphi2 + hae)

        # Get the residuals.
        drho = rho - rho_est
        dz = z - z_est

        # Using the inverse Jacobian, get the residuals in phi and hae.
        dphi = (co*dz - si*drho)/(Rm + hae)
        dhae = (si*dz + co*drho)

        # Adjust the estimated ground latitude and ellipsoidal height.
        phi = phi + dphi
        hae = hae + dhae

    # Get the longitude.
    lam = np.arctan2(y, x)

    # Reduce arrays of length 1 to scalars.
    if phi.size == 1:
        phi = phi.item()
        lam = lam.item()
        hae = hae.item()

    return phi, lam, hae


def geodetic_to_ecef(phi, lam, hae):
    """
    Convert position in geodetic coordinates to ECEF (Earth-centered,
    Earth-fixed) coordinates.  This method is direct and not an approximation.
    This follows the WGS-84 definitions (see WGS-84 Reference System (DMA report
    TR 8350.2)).

    Parameters
    ----------
    phi : float or array_like
        Geodetic latitude in radians.
    lam : float or array_like
        Geodetic longitude in radians.
    hae : float or array_like
        Height above ellipsoid in meters.

    Returns
    -------
    xe, ye, ze : float or array_like
        ECEF x, y, and z-axis position values in meters.

    See Also
    --------
    ecef_to_geodetic

    Notes
    -----
    The distance from the z axis is ::

              .-  a        -.
        rho = |  ---- + hae | cos(phi)
              '- kphi      -'

    where `a` is the semi-major radius of the earth and ::

                  .---------------
                 /     2    2
        kphi =  V 1 - e  sin (phi)
                       E

    The `e sub E` value is the eccentricity of the earth.  Knowing the distance
    from the z axis, we can get the x and y coordinates::

         e                       e
        x  = rho cos(lam)       y  = rho sin(lam) .

    The z-axis coordinate is ::

         e   .-  a         2        -.
        z  = |  ---- (1 - e ) + hae  | sin(phi) .
             '- kphi       E        -'

    Several of these equations are admittedly not intuitively obvious.  The
    interested reader should refer to external texts for insight.

    References
    ----------
    .. [1]  WGS-84 Reference System (DMA report TR 8350.2)
    .. [2]  Inertial Navigation: Theory and Implementation by David Woodburn and
            Robert Leishman
    """

    # Reform the inputs to ndarrays of floats.
    phi = np.asarray(phi).astype(float)
    lam = np.asarray(lam).astype(float)
    hae = np.asarray(hae).astype(float)

    # Get the distance from the z axis.
    kphi = np.sqrt(1 - E2*np.sin(phi)**2)
    rho = (A_E/kphi + hae)*np.cos(phi)

    # Get the x, y, and z coordinates.
    xe = rho*np.cos(lam)
    ye = rho*np.sin(lam)
    ze = (A_E/kphi*(1 - E2) + hae)*np.sin(phi)

    # Reduce arrays of length 1 to scalars.
    if xe.size == 1:
        xe = xe.item()
        ye = ye.item()
        ze = ze.item()

    return xe, ye, ze


def ecef_to_tangent(xe, ye, ze, xe0=None, ye0=None, ze0=None, ned=True):
    """
    Convert ECEF (Earth-centered, Earth-fixed) coordinates, with a defined local
    origin, to local, tangent Cartesian North, East, Down (NED) or East, North,
    Up (ENU) coordinates.

    Parameters
    ----------
    xe, ye, ze : float or array_like
        ECEF x, y, and z-axis position values in meters.
    xe0, ye0, ze0 : float, default 0
        ECEF x, y, and z-axis origin values in meters.
    ned : bool, default True
        Flag to use NED (True) or ENU (False) orientation.

    Returns
    -------
    xt, yt, zt : float or array_like
        Local, tanget x, y, and z-axis position values in meters.

    See Also
    --------
    tangent_to_ecef

    Notes
    -----
    First, the ECEF origin is converted to geodetic coordinates.  Then, those
    coordinates are used to calculate a rotation matrix from the ECEF frame to
    the local, tangent Cartesian frame::

             .-                     -.
         n   |  -sp cl  -sp sl   cp  |
        R  = |    -sl     cl      0  |      NED
         e   |  -cp cl  -cp sl  -sp  |
             '-                     -'

             .-                     -.
         n   |    -sl     cl      0  |
        R  = |  -sp cl  -sp sl   cp  |      ENU
         e   |   cp cl   cp sl   sp  |
             '-                     -'

    where `sp` and `cp` are the sine and cosine of the origin latitude,
    respectively, and `sl` and `cl` are the sine and cosine of the origin
    longitude, respectively.  Then, the displacement vector of the ECEF position
    relative to the ECEF origin is rotated into the local, tangent frame::

        .-  -.      .-        -.
        | xt |    n | xe - xe0 |
        | yt | = R  | ye - ye0 | .
        | zt |    e | ze - ze0 |
        '-  -'      '-        -'

    If `xe0`, `ye0`, and `ze0` are not provided (or are all zeros), the first
    values of `xe`, `ye`, and `ze` will be used as the origin.
    """

    # Reform the inputs to ndarrays of floats.
    xe = np.asarray(xe).astype(float)
    ye = np.asarray(ye).astype(float)
    ze = np.asarray(ze).astype(float)

    # Use the first point as the origin if otherwise not provided.
    if (xe0 == None) and (ye0 == None) and (ze0 == None):
        xe0 = xe[0]
        ye0 = ye[0]
        ze0 = ze[0]

    # Get the local-level coordinates.
    phi0, lam0, _ = ecef_to_geodetic(xe0, ye0, ze0)

    # Get the cosines and sines of the latitude and longitude.
    cp = np.cos(phi0)
    sp = np.sin(phi0)
    cl = np.cos(lam0)
    sl = np.sin(lam0)

    # Get the displacement ECEF vector from the origin.
    dxe = xe - xe0
    dye = ye - ye0
    dze = ze - ze0

    # Get the local, tangent coordinates.
    if ned:
        xt = -sp*cl*dxe - sp*sl*dye + cp*dze
        yt =    -sl*dxe +    cl*dye
        zt = -cp*cl*dxe - cp*sl*dye - sp*dze
    else:
        xt =    -sl*dxe +    cl*dye
        yt = -sp*cl*dxe - sp*sl*dye + cp*dze
        zt =  cp*cl*dxe + cp*sl*dye + sp*dze

    # Reduce arrays of length 1 to scalars.
    if xt.size == 1:
        xt = xt.item()
        yt = yt.item()
        zt = zt.item()

    return xt, yt, zt


def tangent_to_ecef(xt, yt, zt, xe0, ye0, ze0, ned=True):
    """
    Convert local, tangent Cartesian North, East, Down (NED) or East, North, Up
    (ENU) coordinates, with a defined local origin, to ECEF (Earth-centered,
    Earth-fixed) coordinates.

    Parameters
    ----------
    xt, yt, zt : float or array_like
        Local, tanget x, y, and z-axis position values in meters.
    xe0, ye0, ze0 : float, default 0
        ECEF x, y, and z-axis origin values in meters.
    ned : bool, default True
        Flag to use NED or ENU orientation.

    Returns
    -------
    xe, ye, ze : float or array_like
        ECEF x, y, and z-axis position values in meters.

    See Also
    --------
    ecef_to_tangent

    Notes
    -----
    First, the ECEF origin is converted to geodetic coordinates.  Then, those
    coordinates are used to calculate a rotation matrix from the ECEF frame to
    the local, tangent Cartesian frame::

             .-                     -.
         e   |  -sp cl  -sl  -cp cl  |
        R  = |  -sp sl   cl  -cp sl  |      NED
         n   |    cp      0   -sp    |
             '-                     -'

             .-                     -.
         e   |   -sl  -sp cl  cp cl  |
        R  = |    cl  -sp sl  cp sl  |      ENU
         n   |     0    cp     sp    |
             '-                     -'

    where `sp` and `cp` are the sine and cosine of the origin latitude,
    respectively, and `sl` and `cl` are the sine and cosine of the origin
    longitude, respectively.  Then, the displacement vector of the ECEF position
    relative to the ECEF origin is rotated into the local, tangent frame::

        .-  -.      .-  -.   .-   -.
        | xe |    e | xt |   | xe0 |
        | ye | = R  | yt | + | ye0 | .
        | ze |    n | zt |   | ze0 |
        '-  -'      '-  -'   '-   -'

    The scalars `xe0`, `ye0`, and `ze0` defining the origin must be given and
    cannot be inferred.
    """

    # Reform the inputs to ndarrays of floats.
    xt = np.asarray(xt).astype(float)
    yt = np.asarray(yt).astype(float)
    zt = np.asarray(zt).astype(float)

    # Get the local-level coordinates.
    phi0, lam0, _ = ecef_to_geodetic(xe0, ye0, ze0)

    # Get the cosines and sines of the latitude and longitude.
    cp = np.cos(phi0)
    sp = np.sin(phi0)
    cl = np.cos(lam0)
    sl = np.sin(lam0)

    # Get the local, tangent coordinates.
    if ned:
        xe = -sp*cl*xt - sl*yt - cp*cl*zt + xe0
        ye = -sp*sl*xt + cl*yt - cp*sl*zt + ye0
        ze =     cp*xt         -    sp*zt + ze0
    else:
        xe = -sl*xt - sp*cl*yt + cp*cl*zt + xe0
        ye =  cl*xt - sp*sl*yt + cp*sl*zt + ye0
        ze =        +    cp*yt +    sp*zt + ze0

    # Reduce arrays of length 1 to scalars.
    if xe.size == 1:
        xe = xe.item()
        ye = ye.item()
        ze = ze.item()

    return xe, ye, ze


def geodetic_to_curlin(phi, lam, hae, phi0=None, lam0=None, hae0=None,
        ned=True):
    """
    Convert geodetic coordinates with a geodetic origin to local, curvilinear
    position in either North, East, Down (NED) or East, North, Up (ENU)
    coordinates.

    Parameters
    ----------
    phi : float or array_like
        Geodetic latitude in radians.
    lam : float or array_like
        Geodetic longitude in radians.
    hae : float or array_like
        Height above ellipsoid in meters.
    phi0 : float, default None
        Geodetic latitude origin in radians.
    lam0 : float, default None
        Geodetic longitude origin in radians.
    hae0 : float, default None
        Heigh above ellipsoid origin in meters.
    ned : bool, default True
        Flag to use NED (True) or ENU (False) orientation.

    Returns
    -------
    xc, yc, zc : float or array_like
        ECEF x, y, and z-axis position values in meters.

    See Also
    --------
    curlin_to_geodetic

    Notes
    -----
    The equations are ::

        .-  -.   .-                                -.
        | xc |   |     (Rm + hae) (phi - phi0)      |
        | yc | = | (Rt + hae) cos(phi) (lam - lam0) |       NED
        | zc |   |           (hae0 - hae)           |
        '-  -'   '-                                -'

    or ::

        .-  -.   .-                                -.
        | xc |   | (Rt + hae) cos(phi) (lam - lam0) |
        | yc | = |     (Rm + hae) (phi - phi0)      |       ENU
        | zc |   |           (hae - hae0)           |
        '-  -'   '-                                -'

    where ::

                                     2
                             a (1 - e )                 .--------------
              a                      E                 /     2   2
        Rt = ----       Rm = ----------       kphi =  V 1 - e sin (lat) .
             kphi                 3                          E
                              kphi

    Here, `a` is the semi-major axis of the Earth, `e sub E` is the eccentricity
    of the Earth, `Rt` is the transverse radius of curvature of the Earth, and
    `Rm` is the meridional radius of curvature of the Earth.

    If `phi0`, `lam0`, and `hae0` are not provided (are left as `None`), the
    first values of `phi`, `lam`, and `hae` will be used as the origin.

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    .. [2]  https://en.wikipedia.org/wiki/Earth_radius#Meridional
    .. [3]  https://en.wikipedia.org/wiki/Earth_radius#Prime_vertical
    """

    # Reform the inputs to ndarrays of floats.
    phi = np.asarray(phi).astype(float)
    lam = np.asarray(lam).astype(float)
    hae = np.asarray(hae).astype(float)

    # Use the first point as the origin if otherwise not provided.
    if (phi0 == None) and (lam0 == None) and (hae0 == None):
        phi0 = phi[0]
        lam0 = lam[0]
        hae0 = hae[0]

    # Get the parallel and meridional radii of curvature.
    kphi = np.sqrt(1 - E2*np.sin(phi)**2)
    Rt = A_E/kphi
    Rm = A_E*(1 - E2)/kphi**3

    # Get the curvilinear coordinates.
    if ned: # NED
        xc = (Rm + hae)*(phi - phi0)
        yc = (Rt + hae)*np.cos(phi)*(lam - lam0)
        zc = hae0 - hae
    else:   # ENU
        xc = (Rt + hae)*np.cos(phi)*(lam - lam0)
        yc = (Rm + hae)*(phi - phi0)
        zc = hae - hae0

    # Reduce arrays of length 1 to scalars.
    if xc.size == 1:
        xc = xc.item()
        yc = yc.item()
        zc = zc.item()

    return xc, yc, zc


def curlin_to_geodetic(xc, yc, zc, phi0, lam0, hae0, ned=True):
    """
    Convert local, curvilinear position in either North, East, Down (NED) or
    East, North, Up (ENU) coordinates to geodetic coordinates with a geodetic
    origin.  The solution is iterative, using the Newton-Raphson method.

    Parameters
    ----------
    xc, yc, zc : float or array_like
        Navigation-frame x, y, and z-axis position values in meters.
    phi0 : float, default 0
        Geodetic latitude origin in radians.
    lam0 : float, default 0
        Geodetic longitude origin in radians.
    hae0 : float, default 0
        Heigh above ellipsoid origin in meters.
    ned : bool, default True
        Flag to use NED (True) or ENU (False) orientation.

    Returns
    -------
    phi : float or array_like
        Geodetic latitude in radians.
    lam : float or array_like
        Geodetic longitude in radians.
    hae : float or array_like
        Height above ellipsoid in meters.

    See Also
    --------
    geodetic_to_curlin

    Notes
    -----
    The equations to get curvilinear coordinates from geodetic are ::

        .-  -.   .-                                -.
        | xc |   |     (Rm + hae) (phi - phi0)      |
        | yc | = | (Rt + hae) cos(phi) (lam - lam0) |       NED
        | zc |   |           (hae0 - hae)           |
        '-  -'   '-                                -'

    or ::

        .-  -.   .-                                -.
        | xc |   | (Rt + hae) cos(phi) (lam - lam0) |
        | yc | = |     (Rm + hae) (phi - phi0)      |       ENU
        | zc |   |           (hae - hae0)           |
        '-  -'   '-                                -'

    where ::

                                     2
                             a (1 - e )                 .--------------
              a                      E                 /     2   2
        Rt = ----       Rm = ----------       kphi =  V 1 - e sin (lat) .
             kphi                 3                          E
                              kphi

    Here, `a` is the semi-major axis of the Earth, `e sub E` is the eccentricity
    of the Earth, `Rt` is the transverse radius of curvature of the Earth, and
    `Rm` is the meridional radius of curvature of the Earth.  Unfortunately, the
    reverse process to get geodetic coordinates from curvilinear coordinates is
    not as straightforward.  So the Newton-Raphson method is used.  Using NED as
    an example, with the above equations, we can write the differential relation
    as follows::

        .-    -.     .-      -.           .-           -.
        |  dx  |     |  dphi  |           |  J11   J12  |
        |      | = J |        |       J = |             | ,
        |  dy  |     |  dlam  |           |  J21   J22  |
        '-    -'     '-      -'           '-           -'

    where the elements of the Jacobian J are ::

              .-    2        -.
              |  3 e  Rm s c  |
        J11 = |     E         | (phi - phi0) + Rm + h
              | ------------- |
              |        2      |
              '-   kphi      -'

        J12 = 0

              .- .-  2  2     -.         -.
              |  |  e  c       |          |
              |  |   E         |          |
        J21 = |  | ------- - 1 | Rt - hae | s (lam - lam0)
              |  |      2      |          |
              '- '- kphi      -'         -'

        J22 = (Rt + hae) c.

    where `s` and `c` are the sine and cosine of `phi`, respectively.  Using the
    inverse Jacobian, we can get the residuals of `phi` and `lam` from the
    residuals of `xc` and `yc`::

                 J22 dx - J12 dy
        dphi = -------------------
                J11 J22 - J21 J12

                 J11 dy - J21 dx
        dlam = ------------------- .
                J11 J22 - J21 J12

    These residuals are added to the estimated `phi` and `lam` values and
    another iteration begins.

    References
    ----------
    .. [1]  Titterton & Weston, "Strapdown Inertial Navigation Technology"
    .. [2]  https://en.wikipedia.org/wiki/Earth_radius#Meridional
    .. [3]  https://en.wikipedia.org/wiki/Earth_radius#Prime_vertical
    """

    # Reform the inputs to ndarrays of floats.
    xc = np.asarray(xc).astype(float)
    yc = np.asarray(yc).astype(float)
    zc = np.asarray(zc).astype(float)

    # Flip the orientation if it is ENU.
    if not ned:
        zc = zc*(-1)
        temp = xc
        xc = yc*1
        yc = temp*1

    # Define height.
    hae = hae0 - zc

    # Initialize the latitude and longitude.
    phi = phi0 + xc/(A_E + hae)
    lam = lam0 + yc/((A_E + hae)*np.cos(phi))

    # Iterate.
    for _ in range(3):
        # Get the sine and cosine of latitude.
        si = np.sin(phi)
        co = np.cos(phi)

        # Get the parallel and meridional radii of curvature.
        kp2 = 1 - E2*si**2
        kphi = np.sqrt(kp2)
        Rt = A_E/kphi
        Rm = A_E*(1 - E2)/kphi**3

        # Get the estimated xy position.
        xce = (Rm + hae)*(phi - phi0)
        yce = (Rt + hae)*co*(lam - lam0)

        # Get the residual.
        dxc = xc - xce
        dyc = yc - yce

        # Get the inverse Jacobian.
        J11 = (3*E2*Rm*si*co/kp2)*(phi - phi0) + Rm + hae
        J12 = 0
        J21 = ((E2*co**2/kp2 - 1)*Rt - hae)*si*(lam - lam0)
        J22 = (Rt + hae)*co
        Jdet_inv = 1/(J11*J22 - J21*J12)

        # Using the inverse Jacobian, get the residuals in phi and lam.
        dphi = (J22*dxc - J12*dyc)*Jdet_inv
        dlam = (J11*dyc - J21*dxc)*Jdet_inv

        # Update the latitude and longitude.
        phi = phi + dphi
        lam = lam + dlam

    # Reduce arrays of length 1 to scalars.
    if phi.size == 1:
        phi = phi.item()
        lam = lam.item()
        hae = hae.item()

    return phi, lam, hae

