import numpy as np
from numpy.testing import assert_allclose

from astropy.coordinates.matrix_utilities import (
    rotation_matrix as rotation_matrix_astropy)

from nutpy.core.kinematics import rotations as kr


def test_axial_rotation_C():
    """
    Test axial rotation.

    * Orthonormality of rotation matrix
    * Equivalence with astropy rotation
    * Validity with small angles
    """

    angle = np.random.random() * np.pi
    axis = np.random.random((3, 1))
    C_nutpy = kr.axial_rotation_C(axis, angle)

    # Check orthonormality
    det_C_nutpy = np.linalg.det(C_nutpy)

    assert_allclose(abs(det_C_nutpy), 1)

    # Check against astropy
    C_astropy = rotation_matrix_astropy(np.degrees(-angle), axis.flatten()).T

    assert_allclose(C_nutpy, C_astropy), str(C_nutpy)

    # Small angles
    assert_allclose(
        rotation_matrix_astropy(-0.000001, "x").T,
        kr.axial_rotation_C(np.array([1, 0, 0]).reshape(-1, 1), np.deg2rad(0.000001)),
    )


def test_Cx():
    """
    Test Cx orthonormality and compare against general axial rotation
    function.
    """

    theta = np.random.random() * np.pi
    Cx = kr.Cx(theta)

    # Check orthonormality
    det_Cx = np.linalg.det(Cx)

    assert_allclose(abs(det_Cx), 1)

    # Compare against general axial rotation function
    assert_allclose(
        Cx,
        kr.axial_rotation_C(np.array([1, 0, 0]).reshape(-1, 1), theta),
    )


def test_Cy():
    """
    Test Cy orthonormality and compare against general axial rotation
    function.
    """

    theta = np.random.random() * np.pi
    Cy = kr.Cy(theta)

    # Check orthonormality
    det_Cy = np.linalg.det(Cy)

    assert_allclose(abs(det_Cy), 1)

    # Compare against general axial rotation function
    assert_allclose(
        Cy,
        kr.axial_rotation_C(np.array([0, 1, 0]).reshape(-1, 1), theta),
    )


def test_Cz():
    """
    Test Cz orthonormality and compare against general axial rotation
    function.
    """

    theta = np.random.random() * np.pi
    Cz = kr.Cz(theta)

    # Check orthonormality
    det_Cz = np.linalg.det(Cz)

    assert_allclose(abs(det_Cz), 1)

    # Compare against general axial rotation function
    assert_allclose(
        Cz,
        kr.axial_rotation_C(np.array([0, 0, 1]).reshape(-1, 1), theta),
    )


def test_skew():
    """
    Test skew function for single vectors. Compared with handmade
    solution
    """

    v = np.array([[1], [2], [3]])

    M_analytic = np.array([[0, -3, 2],
                           [3, 0, -1],
                           [-2, 1, 0]])
    M = kr.skew(v)

    assert_allclose(M, M_analytic)


def test_skew_ND():
    """
    Test skew function for array of vectors. Compared with handmade
    solution
    """

    v = np.array([[1, 4], [2, 5], [3, 6]])

    M1 = np.array([[0, -3, 2],
                   [3, 0, -1],
                   [-2, 1, 0]])

    M2 = np.array([[0, -6, 5],
                   [6, 0, -4],
                   [-5, 4, 0]])

    M_analytic = np.concatenate((M1[:, :, None], M2[:, :, None]), axis=2)

    M = kr.skew_ND(v)

    assert_allclose(M, M_analytic)


def test_cross_product_skew_1D():
    """
    Test cross product single vectors.

    * Z-axis vector must result from the cross product of X-axis and
    Y-axis vectors
    * Parallel axis shall result in null vector
    """

    e1 = np.array([1, 0, 0]).reshape(-1, 1)
    e2 = np.array([0, 1, 0]).reshape(-1, 1)
    e3 = np.array([0, 0, 1]).reshape(-1, 1)

    v = kr.cross_product_skew(e1, e2)

    u = kr.cross_product_skew(e1, e1)

    assert_allclose(v, e3)
    assert_allclose(u, 0)


def test_cross_product_skew_ND():
    """
    Test cross product for array of vectors.

    * M matrix results from multipliying basis vector to themselves
    (must be 0)
    * B matrix results from multiplying basis vectors in right-handed
    order (must be Q).
    """

    e1 = np.array([1, 0, 0]).reshape(-1, 1)
    e2 = np.array([0, 1, 0]).reshape(-1, 1)
    e3 = np.array([0, 0, 1]).reshape(-1, 1)

    eye_matrix = np.eye(3)
    M = np.concatenate((e2, e3, e1), axis=1)
    Q = np.concatenate((e3, e1, e2), axis=1)

    A = kr.cross_product_skew(eye_matrix, eye_matrix)
    B = kr.cross_product_skew(eye_matrix, M)

    assert_allclose(A, 0)
    assert_allclose(B, Q)


def test_quaternion_modulus_1D():
    """
    Test quaternion modulus function for single vectors
    """

    q = np.array([1, 2, 3, 4]).reshape(-1, 1)

    q_mod_analytic = np.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)

    q_mod = kr.quat_mod(q)[0]

    assert_allclose(q_mod, q_mod_analytic)


def test_quaternion_modulus_ND():
    """
    Test quaternion modulus function for array of vectors.
    Compared with numpy method
    """

    q = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(2, 4).T

    q_mod_numpy = np.linalg.norm(q, axis=0).reshape(1, -1)

    q_mod = kr.quat_mod(q)

    assert_allclose(q_mod, q_mod_numpy)


def test_quaternion_normalization_1D():
    """
    Check quaternion normalization function for single vectors
    """

    q = np.array([1, 2, 3, 4]).reshape(-1, 1)

    q_normalized = kr.quat_norm(q)

    assert_allclose(np.linalg.norm(q_normalized), 1)


def test_quaternion_normalization_ND():
    """
    Check quaternion normalization function for array of vectors
    """

    q = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(2, 4).T

    q_normalized = kr.quat_norm(q)

    q_normalized_mod = np.linalg.norm(q_normalized, axis=0).reshape(1, -1)

    assert_allclose(q_normalized_mod, 1)


def test_quaternion_conjugate_1D():
    """
    Check quaternion conjugation function for single vectors.
    """

    q = np.array([1, 2, 3, 4]).reshape(-1, 1)

    q_star = kr.quat_conj(q)

    v = q[0:3] + q_star[0:3]

    s = q[3] - q_star[3]

    assert_allclose(s, 0)
    assert_allclose(np.linalg.norm(v), 0)


def test_quaternion_conjugate_ND():
    """
    Check quaternion conjugation function for array of vectors
    """

    q = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(2, 4).T

    q_star = kr.quat_conj(q)

    v = np.sum(np.linalg.norm(q[0:3, :] + q_star[0:3, :], axis=0))

    s = np.sum(q[3, :] - q_star[3, :])

    assert_allclose(s, 0)
    assert_allclose(np.linalg.norm(v), 0)


def test_quaternion_inverse_1D():
    """
    Check quaternion inversion function for single vectors
    """

    q = np.array([1, 2, 3, 4]).reshape(-1, 1)

    q_inv = kr.quat_inv(q)

    v = q[0:3] + q_inv[0:3] * np.linalg.norm(q)**2

    s = q[3] - q_inv[3] * np.linalg.norm(q)**2

    assert_allclose(s, 0)
    assert_allclose(np.linalg.norm(v), 0)


def test_quaternion_inverse_ND():
    """
    Check quaternion inversion function for array of vectors
    """

    q = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(2, 4).T

    q_inv = kr.quat_inv(q)

    v = np.sum(np.linalg.norm(q[0:3, :] + q_inv[0:3, :] * np.linalg.norm(q, axis=0)**2, axis=0))

    s = np.sum(q[3, :] - q_inv[3, :] * np.linalg.norm(q, axis=0)**2)

    assert_allclose(s, 0)
    assert_allclose(np.linalg.norm(v), 0)


def test_quaternion_product_1D():
    """
    Check quaternion product function for single vectors. Product of
    quaternion with its conjugate shall return its norm times the
    identity quaternion
    """

    q = np.random.random((4, 1))

    qi = np.array([0, 0, 0, 1]).reshape(-1, 1)

    qm = kr.quat_product(q, kr.quat_conj(q))

    assert_allclose(qm,
                    kr.quat_mod(q)**2 * qi)


def test_quaternion_product_ND():
    """
    Check quaternion product function for array of vectors. Product of
    quaternion with its conjugate shall return its norm times the
    identity quaternion
    """

    q = np.random.random((4, 2))

    qi = np.array([0, 0, 0, 1]).reshape(-1, 1)

    qm = kr.quat_product(q, kr.quat_conj(q))

    assert_allclose(qm,
                    kr.quat_mod(q)**2 * qi)


def test_quaternion_rotation_1D():
    """
    Check rotation using quaternions (single quaternion). Rotation shall
    be equivalent to that provided by rotation matrix.
    """

    u1 = np.random.random((3, 1))

    axis = np.random.random((3, 1))
    axis = axis/np.linalg.norm(axis, axis=0)
    angle = np.random.random() * np.pi

    R = kr.axial_rotation_C(axis, angle).T

    u2 = R @ u1

    v = axis * np.sin(angle/2)
    s = np.array([[np.cos(angle/2)]])
    q = np.concatenate((v, s), axis=0)

    u = kr.quat_rot_v(q, u1)

    assert_allclose(u, u2)


def test_quaternion_rotation_ND():
    """
    Check rotation using quaternions (array of quaternion). Rotation
    shall be equivalent to that provided by rotation matrix.
    """

    u1 = np.random.random((3, 1))

    axes = np.random.random((3, 2))
    axes = axes/np.linalg.norm(axes, axis=0)
    angles = np.random.random(2) * np.pi

    for i in range(2):
        axis = axes[:, [i]]
        angle = angles[i]
        R = kr.axial_rotation_C(axis, angle).T

        u2 = R @ u1

        v = axis * np.sin(angle/2)
        s = np.array([[np.cos(angle/2)]])
        q = np.concatenate((v, s), axis=0)

        u = kr.quat_rot_v(q, u1)

        assert_allclose(u, u2)


def test_quaternion_transform_1D():
    """
    Check quaternion tranformation using quaternions (single quaternion)
    Transformation shall be equivalent to that provided by
    transformtaion matrix.
    """

    u1 = np.random.random((3, 1))

    axis = np.random.random((3, 1))
    axis = axis/np.linalg.norm(axis, axis=0)
    angle = np.random.random() * np.pi

    C = kr.axial_rotation_C(axis, angle)

    u2 = C @ u1

    v = axis * np.sin(angle/2)
    s = np.array([[np.cos(angle/2)]])
    q = np.concatenate((v, s), axis=0)

    u = kr.quat_trans_v(q, u1)

    assert_allclose(u, u2)


def test_quaternion_transform_ND():
    """
    Check quaternion tranformation using quaternions (array of
    quaternion) Transformation shall be equivalent to that provided by
    transformtaion matrix.
    """

    u1 = np.random.random((3, 1))

    axes = np.random.random((3, 2))
    axes = axes/np.linalg.norm(axes, axis=0)
    angles = np.random.random(2) * np.pi

    for i in range(2):
        axis = axes[:, [i]]
        angle = angles[i]
        C = kr.axial_rotation_C(axis, angle)

        u2 = C @ u1

        v = axis * np.sin(angle/2)
        s = np.array([[np.cos(angle/2)]])
        q = np.concatenate((v, s), axis=0)

        u = kr.quat_trans_v(q, u1)

        assert_allclose(u, u2)
