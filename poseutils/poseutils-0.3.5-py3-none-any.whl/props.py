import numpy as np
from tqdm import tqdm

from poseutils.constants import *
from poseutils.common import calc_angle_360
from poseutils.common import normalize_a_to_b

def calculate_limb_lengths(jnts_xd, cvt_mm=False):
    """Calculates every edge/limb length (Euclidean distance) of a 2d or 3d skeleton.

        :param jnts_xd: Joint positions (MxI), M = 14 or 16, I = 2 or 3
        :type jnts_xd: numpy.ndarray
        :param cvt_mm: Convert from meter to milimeters, defaults to False
        :type cvt_mm: bool, optional
        :return: Limb/edge lengths (M-1)
        :rtype: list(float)
    """

    assert len(jnts_xd.shape) == 2
    assert jnts_xd.shape[-1] == 2 or jnts_xd.shape[-1] == 3
    assert jnts_xd.shape[0] == 14 or jnts_xd.shape[0] == 16

    if jnts_xd.shape[0] == 14:
        edge_names = EDGE_NAMES_14JNTS
        edges = EDGES_14
    else:
        edge_names = EDGE_NAMES_16JNTS
        edges = EDGES_16

    edge_length = [0.0]*len(edge_names)
    
    for i, (u, v) in enumerate(edges):
        edge_length[i] = np.linalg.norm(jnts_xd[u]-jnts_xd[v])

    if cvt_mm:
        edge_length = edge_length*1000

    return edge_length

def calculate_avg_limb_lengths(jnts_xd, cvt_mm=False):
    """Calculates aveage edge/limb length (Euclidean distance) of a 2d or 3d skeleton.

        :param jnts_xd: Joint positions (NxMxI), M = 14 or 16, I = 2 or 3
        :type jnts_xd: numpy.ndarray
        :param cvt_mm: Convert from meter to milimeters, defaults to False
        :type cvt_mm: bool, optional
        :return: Avg. Limb/edge lengths (M-1)
        :return: Std. Limb/edge lengths (M-1)
        :return: Limb names
        :rtype: tuple(list(float), list(float), list(str))
    """

    assert len(jnts_xd.shape) == 3
    assert jnts_xd.shape[-1] == 2 or jnts_xd.shape[-1] == 3
    assert jnts_xd.shape[1] == 14 or jnts_xd.shape[1] == 16

    if jnts_xd.shape[1] == 14:
        edge_names = EDGE_NAMES_14JNTS
        edges = EDGES_14
    else:
        edge_names = EDGE_NAMES_16JNTS
        edges = EDGES_16
    
    edge_lengths = []
    
    for i_pt in tqdm(range(jnts_xd.shape[0])):
        jnts = jnts_xd[i_pt, :, :]
        edge_length = [0.0]*len(edge_names)
        
        for i, (u, v) in enumerate(edges):
            edge_length[i] = np.linalg.norm(jnts[u]-jnts[v])
        
        edge_lengths.append(np.array(edge_length))
        
    edge_lengths = np.vstack(edge_lengths)
    
    if cvt_mm:
        edge_lengths = edge_lengths*1000
    
    return np.mean(edge_lengths, axis=0), np.std(edge_lengths, axis=0), edge_names

def calculate_camera_angles(data):
    """Calculates the relative camera angles (elevation and azimuth) w.r.t. body centered axes.

        .. math::

            \\bm{u} &= \\frac{\\bm{p_{ls}} + \\bm{p_{rs}}}{2} - \\bm{p_h} \\\\
            \\bm{\\hat{u}} &= \\frac{\\bm{u}}{|\\bm{u}|} \\\\
            \\bm{f} &= (\\bm{p_{ls}} - \\bm{p_h}) \\times (\\bm{p_{rs}} - \\bm{p_h}) \\\\
            \\bm{\\hat{f}} &= \\frac{\\bm{f}}{|\\bm{f}|} \\\\
            \\bm{r} &= \\bm{\\hat{f}} \\times \\bm{\\hat{u}} \\\\
            \\bm{\\hat{r}} &= \\frac{\\bm{r}}{|\\bm{r}|} \\\\
            \\bm{\\hat{u}} &= \\frac{\\bm{\\hat{r}} \\times \\bm{\\hat{f}}}{|\\bm{\\hat{r}} \\times \\bm{\\hat{f}}|} \\\\
            \\bm{c} &= - \\bm{p_h} \\\\
            e &= 90 - \\frac{180}{\\pi} \\times (\\cos^{-1}(\\bm{\\hat{u}} \\cdot \\bm{c})) \\\\
            \\bm{\\hat{c_u}} &= (\\bm{\\hat{u}} \\cdot \\bm{c}) \\bm{\\hat{u}} \\\\
            \\bm{\\hat{c_{rf}}} &= \\frac{\\bm{c} - \\bm{c_u}}{|\\bm{c} - \\bm{c_u}|} \\\\

        Then calculate the angle around :math: `\\bm{\\hat{u}}`, between two vectors, :math:`\\bm{\\hat{f}}` and :math:`\\bm{\\hat{c_{rf}}}`

        :param data: Joint positions (NxMx3), M = 14 or 16
        :type data: numpy.ndarray
        :return: Array of angles in degrees [0, 360]
        :rtype: numpy.ndarray
    """

    assert len(data.shape) == 3
    assert data.shape[-1] == 3
    assert data.shape[1] == 14 or data.shape[1] == 16
    
    if data.shape[1] == 14:
        ls_idx = 8
        rs_idx = 11
    else:
        ls_idx = 10
        rs_idx = 13

    angles = []
    
    for i in tqdm(range(data.shape[0])):

        hip = data[i, 0, :]
        ls = data[i, ls_idx, :]
        rs = data[i, rs_idx, :]

        h_ls = normalize_a_to_b(hip, ls)
        h_rs = normalize_a_to_b(hip, rs)

        fwd = np.cross(h_ls, h_rs)
        fwd /= np.linalg.norm(fwd)
        
        up = normalize_a_to_b(hip, (ls + rs)/2.0)
        
        right = normalize_a_to_b(np.zeros(3), np.cross(fwd, up))
        
        up = normalize_a_to_b(np.zeros(3), np.cross(right, fwd))
        
        camera_pos = normalize_a_to_b(np.zeros(3), -hip)
        
        camera_elev = 90 - np.degrees(np.arccos(np.dot(up, camera_pos)))
        
        camera_pos_proj_up = np.dot(up, camera_pos)*up
        
        camera_pos_proj_gnd = normalize_a_to_b(camera_pos_proj_up, camera_pos) 
        
        camera_azim = calc_angle_360(fwd, camera_pos_proj_gnd, up)

        angles.append(np.array([camera_elev, camera_azim]))
        
    return np.array(angles)

def get_body_centered_axes(joints):
    """Calculates and returns body centered axes - right, up and forward vectors of the skeleton.

        .. math::

            \\bm{u} &= \\frac{\\bm{p_{ls}} + \\bm{p_{rs}}}{2} - \\bm{p_h} \\\\
            \\bm{\\hat{u}} &= \\frac{\\bm{u}}{|\\bm{u}|} \\\\
            \\bm{f} &= (\\bm{p_{ls}} - \\bm{p_h}) \\times (\\bm{p_{rs}} - \\bm{p_h}) \\\\
            \\bm{\\hat{f}} &= \\frac{\\bm{f}}{|\\bm{f}|} \\\\
            \\bm{r} &= \\bm{\\hat{f}} \\times \\bm{\\hat{u}} \\\\
            \\bm{\\hat{r}} &= \\frac{\\bm{r}}{|\\bm{r}|} \\\\
            \\bm{f} &= (\\bm{p_{ls}} - \\bm{p_h}) \\times (\\bm{p_{rs}} - \\bm{p_h}) \\\\
            \\bm{\\hat{f}} &= \\frac{\\bm{f}}{|\\bm{f}|} \\\\
            R &= [\\bm{\\hat{r}} \\; \\bm{\\hat{u}} \\; \\bm{\\hat{f}}]


        :param joints: Joint positions (NxMx3), M = 14 or 16
        :type joints: numpy.ndarray
        :return:
            - up: Up vectors (Nx3x1)
            - forward: Forward vectors (Nx3x1)
            - right: Right vectors (Nx3x1)
            - R: Rotation/set of axes matrix (Nx3x3)
        :rtype: tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """

    assert len(joints.shape) == 3
    assert joints.shape[-1] == 3
    assert joints.shape[1] == 14 or joints.shape[1] == 16

    hip = 0
    if joints.shape[1] == 14:
        lshldr = 8
        rshldr = 11
    else:
        lshldr = 10
        rshldr = 13

    p_p = joints[:, hip, :]
    p_l = joints[:, lshldr, :]
    p_r = joints[:, rshldr, :]

    up = ((p_l + p_r) / 2.) - p_p
    up = up / np.linalg.norm(up, axis=1).reshape(-1, 1)

    forward = np.cross((p_l - p_p), (p_r - p_p))
    forward = forward / np.linalg.norm(forward, axis=1).reshape(-1, 1)
    
    right = np.cross(forward, up, axis=1)
    right = right / np.linalg.norm(right, axis=1).reshape(-1, 1)

    forward = np.cross(up, right, axis=1)
    forward = forward / np.linalg.norm(forward, axis=1).reshape(-1, 1)

    R = np.hstack((right.reshape((-1, 1, 3)), up.reshape((-1, 1, 3)), forward.reshape((-1, 1, 3))))

    assert R.shape[1] == 3
    assert R.shape[2] == 3

    return up, forward, right, R.transpose((0, 2, 1))

def get_angles_from_joints(joints):
    """Convert skeleton from positions to inter-joint angles

        :param joints: Joint positions (Mx3), M = 14 or 16
        :type joints: numpy.ndarray
        :raises ValueError: If anyother joint configuration is specified
        :return:
            - joint_angles: Inter-joint angles
            - edge_names: Edge/limb names
        :rtype: tuple(numpy.ndarray, numpy.ndarray)
    """

    assert len(joints.shape) == 2
    assert joints.shape[-1] == 3
    
    if joints.shape[0] == 16:
        edges = EDGES_16
        edge_names = EDGE_NAMES_16JNTS
    elif joints.shape[0] == 14:
        edges = EDGES_14
        edge_names = EDGE_NAMES_14JNTS
    else:
        raise ValueError("Only supports 14 or 16 joint configuration. Has to be of shape (14, 3) or (16, 3)")

    joint_angles = []
    
    for u, v in edges:
        
        vec = normalize_a_to_b(joints[u], joints[v])
        angles = [np.arccos(vec[0]), np.arccos(vec[1]), np.arccos(vec[2])]
        joint_angles.append(angles)
    
    return np.array(joint_angles), np.array(edge_names)

def get_joints_from_angles(angles, bone_lengths):
    """Convert inter-joint angles to positions

        :param angles: Array of angles in degrees (M-1)x3
        :type angles: numpy.ndarray
        :param bone_lengths: Array of bone lengths (M-1)x1
        :type bone_lengths: numpy.ndarray
        :raises ValueError: If anyother joint configuration is specified
        :return: Joint positions (Mx3), root centered
        :rtype: numpy.ndarray
    """

    assert len(angles.shape) == 2
    assert angles.shape[-1] == 3

    if angles.shape[0] == 15:
        edges = EDGES_16
    elif angles.shape[0] == 13:
        edges = EDGES_14
    else:
        raise ValueError("Only 14 or 16 joint configurations.")

    adjacency = adjacency_list(angles.shape[0]+1)

    queue = []

    queue.append(0)

    joints = []

    for _ in range(angles.shape[0]+1):
        joints.append(np.zeros(3))

    while len(queue) > 0:
        current = queue.pop(0)

        for child in adjacency[current]:
            queue.append(child)
            idx = edges.index([current, child])
            angle = np.array(angles[idx])
            vec = np.array([np.cos(angle[0]), np.cos(angle[1]), np.cos(angle[2])])
            joints[child] = bone_lengths[idx]*vec + joints[current]
    
    return np.array(joints)

def get_bounding_box_2d(joints):
    """Get 2d bounding box

        :param joints: Joint positions (NxMx2)
        :type joints: numpy.ndarray
        :return: 
            - left_x: Array of x coordinates of left side
            - left_y: Array of y coordinates of left side
            - right_x: Array of x coordinates of right side
            - right_y: Array of y coordinates of right side
        :rtype: tuple(numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """

    assert joints.shape[-1] == 2
    assert len(joints.shape) == 3

    left_x = np.min(joints[:, :, 0], axis=1)-50
    left_y = np.min(joints[:, :, 1], axis=1)-50
    right_x = np.max(joints[:, :, 0], axis=1)+50
    right_y = np.max(joints[:, :, 1], axis=1)+50

    return left_x, left_y, right_x, right_y

def get_edm(joints, square_form=False):
    """Returns a NxMxM euclidean distance matrix or just the upper triangle Nx(Mx(M-1))/2

        :param joints: Joint positions (NxMx2)
        :type joints: numpy.ndarray
        :param square_form: Whether to return the full distance matrix, defaults to False
        :type square_form: bool, optional
        :return: Array of the upper triangle of the distance matrix (Nx(Mx(M-1))/2) or the full Euclidean distance matrix (NxMxM)
        :rtype: numpy.ndarray
    """

    assert joints.shape[-1] == 3 or joints.shape[-1] == 2

    joints_ = joints.copy()

    joints_ = joints_[:, :, :, np.newaxis]

    square_diff = (joints_ - joints_.transpose(0, 3, 2, 1))**2

    edm = np.sqrt(np.sum(square_diff, axis=2))

    if square_form:
        return edm

    else:
        indices = np.triu_indices(14, k=1)
        return edm[:, indices[0], indices[1]]