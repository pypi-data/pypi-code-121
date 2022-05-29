smpl_path = ""
JOINT_REGRESSOR_TRAIN_EXTRA = smpl_path + 'J_regressor_extra.npy'
JOINT_REGRESSOR_H36M_correct = smpl_path + 'J_regressor_h36m_correct.npy'
SMPL_FILE = smpl_path + 'basicModel_neutral_lbs_10_207_0_v1.0.0.pkl'
SMPL_Male = smpl_path + 'basicModel_m_lbs_10_207_0_v1.0.0.pkl'
SMPL_Female = smpl_path + 'basicModel_f_lbs_10_207_0_v1.0.0.pkl'
SMPL_sampling_matrix = smpl_path + 'mesh_downsampling.npz'
MANO_FILE = smpl_path + 'MANO_RIGHT.pkl'
MANO_sampling_matrix = smpl_path + 'mano_downsampling.npz'

JOINTS_IDX = [
    8, 5, 29, 30, 4, 7, 21, 19, 17, 16, 18, 20, 31, 32, 33, 34, 35, 36, 37, 24,
    26, 25, 28, 27
]
"""
We follow the body joint definition, loss functions, and evaluation metrics from 
open source project GraphCMR (https://github.com/nkolot/GraphCMR/)

Each dataset uses different sets of joints.
We use a superset of 24 joints such that we include all joints from every dataset.
If a dataset doesn't provide annotations for a specific joint, we simply ignore it.
The joints used here are:
"""

SMPL_J24_IDX = {
    "right_ankle": 0,
    "right_knee": 1,
    "right_hip": 2,
    "left_hip": 3,
    "left_knee": 4,
    "left_ankle": 5,
    "right_wrist": 6,
    "right_elbow": 7,
    "right_shoulder": 8,
    "left_shoulder": 9,
    "left_elbow": 10,
    "left_wrist": 11,
    "neck": 12,
    "top_of_head": 13,
    "pelvis": 14,
    "thorax": 15,
    "spine": 16,
    "jaw": 17,
    "head": 18,
    "nose": 19,
    "left_eye": 20,
    "right_eye": 21,
    "left_ear": 22,
    "right_ear": 23,
}
#  [14, 3, 4, 5, 2, 1, 0, 16, 12, 17, 18, 9, 10, 11, 8, 7, 6]
COMMON_J12_IDX = {
    "right_ankle": 0,
    "right_knee": 1,
    "right_hip": 2,
    "left_hip": 3,
    "left_knee": 4,
    "left_ankle": 5,
    "right_wrist": 6,
    "right_elbow": 7,
    "right_shoulder": 8,
    "left_shoulder": 9,
    "left_elbow": 10,
    "left_wrist": 11,
}

BODY_EDGE_LIST = [
    ["right_ankle", "right_knee"],
    ["right_knee", "right_hip"],
    ["right_hip", "right_shoulder"],
    ["right_shoulder", "right_elbow"],
    ["right_elbow", "right_wrist"],

    ["left_ankle", "left_knee"],
    ["left_knee", "left_hip"],
    ["left_hip", "left_shoulder"],
    ["left_shoulder", "left_elbow"],
    ["left_elbow", "left_wrist"],
]

J14_IDX = {
    "right_ankle": 0,
    "right_knee": 1,
    "right_hip": 2,
    "left_hip": 3,
    "left_knee": 4,
    "left_ankle": 5,
    "right_wrist": 6,
    "right_elbow": 7,
    "right_shoulder": 8,
    "left_shoulder": 9,
    "left_elbow": 10,
    "left_wrist": 11,
    "neck": 12,
    "head": 13,
}
COCO_J17_IDX = {
    "nose": 0,
    "left_eye": 1,
    "right_eye": 2,
    "left_ear": 3,
    "right_ear": 4,
    "left_shoulder": 5,
    "right_shoulder": 6,
    "left_elbow": 7,
    "right_elbow": 8,
    "left_wrist": 9,
    "right_wrist": 10,
    "left_hip": 11,
    "right_hip": 12,
    "left_knee": 13,
    "right_knee": 14,
    "left_ankle": 15,
    "right_ankle": 16,
}

COCO_Skeleton = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]


MPII_J16_IDX = {
    "right_ankle": 0,
    "right_knee": 1,
    "right_hip": 2,
    "left_hip": 3,
    "left_knee": 4,
    "left_ankle": 5,
    "pelvis": 6,
    "thorax": 7,
    "neck": 8,
    "top_of_head": 9,
    "right_wrist": 10,
    "right_elbow": 11,
    "right_shoulder": 12,
    "left_shoulder": 13,
    "left_elbow": 14,
    "left_wrist": 15,
}
H36M_J17_IDX = {
    "pelvis": 0,
    "right_hip": 1,
    "right_knee": 2,
    "right_ankle": 3,
    "left_hip": 4,
    "left_knee": 5,
    "left_ankle": 6,
    "torso": 7,
    "neck": 8,
    "nose": 9,
    "head": 10,
    "left_shoulder": 11,
    "left_elbow": 12,
    "left_wrist": 13,
    "right_shoulder": 14,
    "right_elbow": 15,
    "right_wrist": 16,
}

def convert_idx(from_idx, to_idx):
    index_list = []
    for i, name in enumerate(to_idx):
        assert to_idx[name] == i
        index_list.append(from_idx[name])
    return index_list

SMPL_TO_COCO = convert_idx(SMPL_J24_IDX, COCO_J17_IDX)
SMPL_TO_MPII = convert_idx(SMPL_J24_IDX, MPII_J16_IDX)
SMPL_TO_J14 = convert_idx(SMPL_J24_IDX, J14_IDX)
SMPL_TO_J12 = convert_idx(SMPL_J24_IDX, COMMON_J12_IDX)
H36M_TO_J14 = convert_idx(H36M_J17_IDX, J14_IDX)
H36M_TO_J12 = convert_idx(H36M_J17_IDX, COMMON_J12_IDX)
COCO_TO_J12 = convert_idx(COCO_J17_IDX, COMMON_J12_IDX)

# print("SMPL_TO_J12", SMPL_TO_J12)
# print("COCO_TO_J12", COCO_TO_J12)
# COCO_TO_J14 = convert_idx(COCO_J17_IDX, J14_IDX)
# MPII_J16_NAME = ("R_Ankle", "R_Knee", "R_Hip", "L_Hip", "L_Knee", "L_Ankle",
#                  "Pelvis", "Thorax", "Neck", "Top_of_Head", "R_Wrist",
#                  "R_Elbow", "R_Shoulder", "L_Shoulder", "L_Elbow", "L_Wrist")
# J24_TO_MPII = [J24_NAME.index(name) for name in MPII_J16_NAME]

H36M_J17_NAME = ('Pelvis', 'R_Hip', 'R_Knee', 'R_Ankle', 'L_Hip', 'L_Knee',
                 'L_Ankle', 'Torso', 'Neck', 'Nose', 'Head', 'L_Shoulder',
                 'L_Elbow', 'L_Wrist', 'R_Shoulder', 'R_Elbow', 'R_Wrist')
J24_TO_J14 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 18]
H36M_J17_TO_J14 = [3, 2, 1, 4, 5, 6, 16, 15, 14, 11, 12, 13, 8, 10]

J14_NAME = [H36M_J17_NAME[idx] for idx in H36M_J17_TO_J14]
# print("J14_NAME", J14_NAME)
"""
We follow the hand joint definition and mesh topology from 
open source project Manopth (https://github.com/hassony2/manopth)

The hand joints used here are:
"""
J_NAME = ('Wrist', 'Thumb_1', 'Thumb_2', 'Thumb_3', 'Thumb_4', 'Index_1',
          'Index_2', 'Index_3', 'Index_4', 'Middle_1', 'Middle_2', 'Middle_3',
          'Middle_4', 'Ring_1', 'Ring_2', 'Ring_3', 'Ring_4', 'Pinky_1',
          'Pinky_2', 'Pinky_3', 'Pinky_4')
ROOT_INDEX = 0
