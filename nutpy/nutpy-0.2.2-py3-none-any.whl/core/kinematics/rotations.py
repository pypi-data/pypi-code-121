import numpy as np
from nutpy import numeric as nm


def axial_rotation_C(u, theta):
    """
    Creates coordinate rotation matrix from direction and angle.

    Parameters
    ----------
    u : ndarray (3,1)
        Direction of rotation.
    theta : float
        Rotated angle (rad).

    Returns
    -------
    C : ndarray (3,3)
        Resulting coordinate rotation matrix.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Rotation_matrix#Rotation_matrix_from_axis_and_angle
    """

    u_unit = u/nm.norm(u)

    R = np.cos(theta) * np.eye(3) + np.sin(theta) * skew(u_unit) + (1 - np.cos(theta)) * (u_unit @ u_unit.T)

    C = R.T

    return C


def Cx(theta):
    """
    Coordinate rotation around X-axis.

    This matrix transforms the coordinates of a vector from a reference system (S1) to a
    rotated one (S2) (u2 = C @ u1). S2 is obtained rotating S1 an angle theta around X-axis.

    Parameters
    ----------
    theta : float
        Rotated angle (rad).

    Returns
    -------
    C : ndarray (3,3)
        Coordinate rotation matrix around X-axis.

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    C = np.array([[1,              0,             0],
                  [0,  np.cos(theta), np.sin(theta)],
                  [0, -np.sin(theta), np.cos(theta)]])

    return C


def Cy(theta):
    """
    Coordinate rotation around Y-axis.

    This matrix transforms the coordinates of a vector from a reference system (S1) to a
    rotated one (S2) (u2 = C @ u1). S2 is obtained rotating S1 an angle theta around Y-axis.

    Parameters
    ----------
    theta : float
        Rotated angle (rad).

    Returns
    -------
    C : ndarray (3,3)
        Coordinate rotation matrix around Y-axis.

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    C = np.array([[np.cos(theta), 0, -np.sin(theta)],
                  [0,             1,              0],
                  [np.sin(theta), 0, np.cos(theta)]])

    return C


def Cz(theta):
    """
    Coordinate rotation around Z-axis.

    This matrix transforms the coordinates of a vector from a reference system (S1) to a
    rotated one (S2) (u2 = C @ u1). S2 is obtained rotating S1 an angle theta around Z-axis.

    Parameters
    ----------
    theta : float
        Rotated angle (rad).

    Returns
    -------
    C : ndarray (3,3)
        Coordinate rotation matrix around Z-axis.

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    C = np.array([[np.cos(theta), np.sin(theta), 0],
                  [-np.sin(theta), np.cos(theta), 0],
                  [0,              0,             1]])

    return C


def Rx(theta):
    """
    Rotation around X-axis.

    This matrix rotates a vector an angle theta around X-axis.

    Parameters
    ----------
    theta : float
        Rotated angle (rad).

    Returns
    -------
    R : ndarray (3,3)
        Rotation matrix around X-axis.

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    R = Cx(theta).T

    return R


def Ry(theta):
    """
    Rotation around Y-axis.

    This matrix rotates a vector an angle theta around Y-axis.

    Parameters
    ----------
    theta : float
        Rotated angle (rad).

    Returns
    -------
    R : ndarray (3,3)
        Rotation matrix around Y-axis.

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    R = Cy(theta).T

    return R


def Rz(theta):
    """
    Rotation around Z-axis.

    This matrix rotates a vector an angle theta around Z-axis.

    Parameters
    ----------
    theta : float
        Rotated angle (rad).

    Returns
    -------
    R : ndarray (3,3)
        Rotation matrix around Z-axis.

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    R = Cz(theta).T

    return R


def qx(theta):
    """
    X-axis angel quaternion.

    Expresses the attitude of a body (Sb) which is rotated an angle theta about X-axis
    regarding a reference system (S0).

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    theta : float/list/1D-array (n)
        Rotated angle about X-axis

    Returns
    -------
    q : ndarray (4,n)
        Output quaternion (scalar part at the bottom)

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    theta_ar = np.asarray([theta]).flatten()
    n = len(theta_ar)
    q = np.zeros((4, n))

    q[0, :] = np.sin(theta_ar/2)
    q[3, :] = np.cos(theta_ar/2)

    return q


def qy(theta):
    """
    Y-axis angel quaternion.

    Expresses the attitude of a body (Sb) which is rotated an angle theta about Y-axis
    regarding a reference system (S0).

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    theta : float/list/1D-array (n)
        Rotated angle about Y-axis

    Returns
    -------
    q : ndarray (4,n)
        Output quaternion (scalar part at the bottom)

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    theta_ar = np.asarray([theta]).flatten()
    n = len(theta_ar)
    q = np.zeros((4, n))

    q[1, :] = np.sin(theta_ar/2)
    q[3, :] = np.cos(theta_ar/2)

    return q


def qz(theta):
    """
    Z-axis angel quaternion.

    Expresses the attitude of a body (Sb) which is rotated an angle theta about Z-axis
    regarding a reference system (S0).

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    theta : float/list/1D-array (n)
        Rotated angle about Z-axis

    Returns
    -------
    q : ndarray (4,n)
        Output quaternion (scalar part at the bottom)

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    theta_ar = np.asarray([theta]).flatten()
    n = len(theta_ar)
    q = np.zeros((4, n))

    q[2, :] = np.sin(theta_ar/2)
    q[3, :] = np.cos(theta_ar/2)

    return q


def euler_rotation_sequence_C(phi, theta, psi, sequence):
    """
    Creates coordinate rotation matrix from euler angles

    The first rotation is of an angle psi about the k-axis, the second
    rotation is an angle theta about the j-axis and the third rotation
    an angle phi about the i-axis.

    Rijk(phi, theta, psi) = Ri(phi)Rj(theta)Rk(psi)

    Parameters
    ----------
    phi : float
        Third rotated angle (rad)
    theta : float
        Second rotated angle (rad)
    psi : float
        First rotated angle (rad)
    sequence : str
        Sequence of rotation (order of axis) '123', '231', etc

    Returns
    -------
    C : ndarray (3,3)
        Resulting coordinate rotation matrix

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16), 1-35.
    """

    axis_dict = {'1': Cx, '2': Cy, '3': Cz}
    euler_vector = np.array([phi, theta, psi])

    C = np.eye(3)

    for idx, axis in enumerate(sequence):
        C = axis_dict[axis](euler_vector[idx]) @ C

    return C


def euler_rotation_sequence_q(phi, theta, psi, sequence):
    """
    Creates quaternion rotation from euler angles

    The first rotation is of an angle psi about the k-axis, the second
    rotation is an angle theta about the j-axis and the third rotation
    an angle phi about the i-axis.

    qijk(phi, theta, psi) = qi(phi)qj(theta)qk(psi)

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    phi : float
        Third rotated angle (rad)
    theta : float
        Second rotated angle (rad)
    psi : float
        First rotated angle (rad)
    sequence : str
        Sequence of rotation (order of axis) '123', '231', etc

    Returns
    -------
    q : ndarray (4,n)
        Resulting quaternion (scalar part at the bottom)

    References
    ----------
    .. [1] Diebel, J. (2006). Representing attitude: Euler angles,
           unit quaternions, and rotation vectors. Matrix, 58(15-16),
           1-35.
    """

    axis_dict = {'1': qx, '2': qy, '3': qz}
    euler_vector = np.array([phi, theta, psi])

    q = np.array([0, 0, 0, 1]).reshape(-1, 1)

    for idx, axis in enumerate(sequence):
        q = quat_product(axis_dict[axis](euler_vector[idx]), q)

    return q


def instant_attitude_C(SSP, t):
    """
    Calculates instantaneus attitude matrix of the spacecraft

    Euler angles sequence 1-3-1
    The attitude matrix is expressed as a coordinate transformation
    matrix. Note that the nomenclatures of the angles differ:
    (phi, theta, psi) -> (psi, alpha, phi)

    Parameters
    ----------
    SSP : list
        Scan Strategy Parameters (alpha (deg), beta (deg), spin period
        (min), precesion period (min))
    t : float
        Instant of interest

    Returns
    -------
    C : ndarray (3,3)
        Attitude matrix expressedd as a coordinate transformation matrix

    References
    ----------
    .. [1] Scan article
    """

    alpha = SSP[0] * np.pi/180
    T_spin = SSP[2]
    T_prec = SSP[3]

    # phi is the spin angle
    phi = (2 * np.pi/(T_spin * 60)) * t

    # psi is the precession angle
    psi = (2 * np.pi/(T_prec * 60)) * t

    C = euler_rotation_sequence_C(psi, alpha, phi, '131')

    return C


def instant_attitude_q(SSP, t):
    """
    Calculates instantaneus attitude quaternion of the spacecraft

    Euler angles sequence 1-3-1, order ->
    Note that the nomenclatures of the angles here and in used function
    differ: (phi, theta, psi) -> (psi, alpha, phi)

    Parameters
    ----------
    SSP : list
        Scan Strategy Parameters (alpha (deg), beta (deg), spin period
        (min), precesion period (min))
    t : float/list/1D-array (n)
        Instants of interest

    Returns
    -------
    q : ndarray (4,n)
        Attitude matrix expressedd as a quaternion (scalar part at the
        bottom)

    References
    ----------
    .. [1] Scan article
    """

    alpha = SSP[0] * np.pi/180
    T_spin = SSP[2]
    T_prec = SSP[3]

    # phi is the spin angle
    phi = (2 * np.pi/(T_spin * 60)) * t

    # psi is the precession angle
    psi = (2 * np.pi/(T_prec * 60)) * t

    # alpha as array
    alpha = alpha * np.ones_like(psi)

    q = euler_rotation_sequence_q(psi, alpha, phi, '131')

    return q


def emulate_attitude(tf, dT, q0, SSP):
    """
    Propagates the attitude of the spacecraft

    Parameters
    ----------
    tf : float
        End time of propagation (s)
    dT : float
        Step time for propagation (s)
    q0 : ndarray (4,1)
        Initial attitude quaternion
    SSP : list
        Scan Strategy Parameters (alpha (deg), beta (deg), spin period
        (min), precesion period (min))
    bar : bool
        If True, shows progress bar

    Returns
    -------
    time : 1-D array
        Discretized time used for propagation
    q : ndarray (4,n)
        Attitude in each time step
    """

    time = np.arange(0, tf + dT, dT)

    q = instant_attitude_q(SSP, time)

    if q0 is None:
        pass
    else:
        q = quat_product(q, q0)

    return time, q


def pointing(attitude_df, u0):
    """
    Calculates pointing direction of a vector for a given attitude

    Parameters
    ----------
    attitude_df : pandas DataFrame
        Attitude of body frame over time expressed as quaternions
    u0 : ndarray (3,n)
        Pointing direction in body frame

    Returns
    -------
    time : 1D-darray (n)
        Time
    u : ndarray (3,n)
        Pointing over time
    """

    q = attitude_df.values.T

    time = attitude_df.index.values

    u = quat_rot_v(q, u0)

    return time, u


def q2C(q):
    """
    Generates attitude matrix from quaternion

    Parameters
    ----------
    q : ndarray (4x1)
        Input quaternion

    Returns
    -------
    C : ndarray (3x3)
        Output attitude matrix

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    s = q[3]
    e = q[0:3, :]

    C = ((s ** 2 - np.linalg.norm(e)**2) * np.eye(3)
         - 2 * s * skew_ND(e) + 2 * e @ e.T)

    return C


def C2q(C):
    """
    Generates quaternion from attitude matrix

    Parameters
    ----------
    C : ndarray (3x3)
        Input attitude matrix

    Returns
    -------
    q : ndarray (4x1)
        Output quaternion

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    a11, a12, a13 = C[0, :]
    a21, a22, a23 = C[1, :]
    a31, a32, a33 = C[2, :]

    trA = np.trace(C)

    v = np.array([1 + 2 * a11 - trA,
                  1 + 2 * a22 - trA,
                  1 + 2 * a33 - trA,
                  1 + trA])

    idx = v.argmax()

    if idx == 0:
        a = 1
        b = (a12 + a21)/v[0]
        c = (a13 + a31)/v[0]
        d = (a23 - a32)/v[0]

    elif idx == 1:
        a = (a21 + a12)/v[1]
        b = 1
        c = (a23 + a32)/v[1]
        d = (a31 - a13)/v[1]

    elif idx == 2:
        a = (a31 + a13)/v[2]
        b = (a32 + a23)/v[2]
        c = 1
        d = (a12 - a21)/v[2]

    elif idx == 3:
        a = (a23 - a32)/v[3]
        b = (a31 - a13)/v[3]
        c = (a12 - a21)/v[3]
        d = 1

    q = quat_norm((1/4) * np.array([a, b, c, d]).reshape(-1, 1))

    return q


def quat_product(q1, q2):
    """
    Carry out quaternion product

    q3 = q1 x q2
    qC<-A = qC<-B x qB<-A

    It's compatible to combine (4,1) with (4,n)

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q1 : ndarray (4,n)
        Input quaternion
    q2 : ndarray (4,n)
        Input quaternion

    Returns
    -------
    q3 : ndarray (4,n)
        Output quaternion

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    v1 = q1[0:3, :]
    v2 = q2[0:3, :]

    s1 = q1[[3], :]
    s2 = q2[[3], :]

    _, n = q1.shape
    s3 = np.zeros((1, n))

    # these are dot products
    s_a = np.einsum('ij,ij->ij', s1, s2)
    s_b = np.einsum('ij,ij->j', v1, v2).reshape(1, -1)

    s3 = s_a - s_b

    v3 = s1 * v2 + s2 * v1 - cross_product_skew(v1, v2)

    q3 = np.concatenate((v3, s3), axis=0)

    return q3


def cross_product_skew(u, v):
    """
    Calculates cross product of vector using skew matrix

    q = u x v = skew(u) @ v
    matrix product in einsum is 'ij,j...->i...', with a third dimension
    (n different products) is 'ijn,jn->in'

    It's compatible to combine (4,1) with (4,n)

    Parameters
    ----------
    u : ndarray (3,n)
        Input vector
    v : ndarray (3,n)
    Input vector

    Returns
    -------
    w : ndarray (3,n)
        output vector
    """

    M = skew_ND(u)

    w = np.einsum('ijn,jn->in', M, v)

    return w


def skew(v):
    """
    Generates skew matrix from vector

    Parameters
    ----------
    v : ndarray (3,1)
        Input vector

    Returns
    -------
    M : ndarray (3,3)
        Skew matrix from vector
    """

    M = np.zeros((3, 3))

    M[0, 1] = -v[2]
    M[0, 2] = v[1]
    M[1, 0] = v[2]
    M[1, 2] = -v[0]
    M[2, 0] = -v[1]
    M[2, 1] = v[0]

    return M


def skew_ND(v):
    """
    Generates skew matrix from vector

    For inputs with n>1, skew matrices are concatenated along axis 1
    (3,3n) (easy to implement) and then reordered into (3,3,n) (easy to
    use).

    Parameters
    ----------
    v : ndarray (3,n)
        Input vector

    Returns
    -------
    M : ndarray (3,3,n)
        Skew matrix from vector
    """

    _, n = v.shape

    v1 = v[:1, :]
    v2 = v[1:2, :]
    v3 = v[2:3, :]

    M = np.zeros((3, 3*n))

    M[:1, 1::3] = -v3
    M[:1, 2::3] = v2

    M[1:2, ::3] = v3
    M[1:2, 2::3] = -v1

    M[2:3, ::3] = -v2
    M[2:3, 1::3] = v1

    M = M.reshape(3, 3, n, order='F')

    return M


def quat_rot_v(q, v):
    """
    Rotates vector according to provided quaternion. Same rotation as
    experienced from A to B frame

    vB = qB<-A x vA x q*B<-A

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q : ndarray (4,n)
        attitude quaternion
    v : ndarray (3,1)
        Input vector

    Returns
    -------
    v_B : ndarray (3,n)
        Rotated vector

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    _, n = q.shape

    z = np.zeros((1, 1))

    q_v_A = np.concatenate((v, z), axis=0)

    q_v_A_ext = np.repeat(q_v_A, n, axis=1)

    q_v_B = quat_product(quat_product(quat_conj(q), q_v_A_ext), q)

    v_B = q_v_B[0:3, :]

    return v_B


def quat_trans_v(q, v):
    """
    Transform vector coordinates according to provided quaternion

    vB = qB<-A x vA x q*B<-A

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q : ndarray (4xn)
        Attitude quaternion
    v : ndarray (3x1)
        Input vector coordinates

    Returns
    -------
    v_B : ndarray (3xn)
        Transformed vector coordinates

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    _, n = q.shape

    z = np.zeros((1, 1))

    q_v_A = np.concatenate((v, z), axis=0)

    q_v_A_ext = np.repeat(q_v_A, n, axis=1)

    q_v_B = quat_product(quat_product(q, q_v_A_ext), quat_conj(q))

    v_B = q_v_B[0:3, :]

    return v_B


def quat_conj(q):
    """
    Calculates quaternion conjugate

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q : ndarray (4,n)
        Input quaternion

    Returns
    -------
    q_star : ndarray (4,n)
        Output quaternion

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    v = -q[0:3, :]

    s = q[[3], :]

    q_star = np.concatenate((v, s), axis=0)

    return q_star


def quat_mod(q):
    """
    Calculates quaternion module

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q : ndarray (4xn)
        Input quaternion

    Returns
    -------
    mod_ar : ndarray (1xn)
        Array with the modulus of each quaternion

    """

    qx = q[[0], :]
    qy = q[[1], :]
    qz = q[[2], :]
    qs = q[[3], :]

    mod_ar = np.sqrt(qs ** 2 + qx ** 2 + qy ** 2 + qz ** 2)

    return mod_ar


def quat_inv(q):
    """
    Calculates quaternion inverse

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q : ndarray (4xn)
        Input quaternion

    Returns
    -------
    q_inv : ndarray (4xn)
        Output quaternion

    References
    ----------
    .. [1] Markley, F. L., & Crassidis, J. L. (2014). Fundamentals of
           spacecraft attitude determination and control (Vol. 33).
           New York: Springer.
    """

    q_inv = quat_conj(q)/quat_mod(q)**2

    return q_inv


def quat_norm(q):
    """
    Normalizes quaternion

    Quaternion order: scalar part at the bottom of the vector

    Parameters
    ----------
    q : ndarray (4xn)
        Input quaternion

    Returns
    -------
    q_norm : ndarray (4xn)
        Normalized quaternion

    """

    q_norm = q/quat_mod(q)

    return q_norm
