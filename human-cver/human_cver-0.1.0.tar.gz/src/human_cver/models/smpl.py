import os.path as osp

import numpy as np
import smplx
import torch
import torch.nn as nn
from smplx.lbs import vertices2joints

from ..keypoints.human import JOINTS_IDX as SMPL_J24


class BaseSMPL(smplx.SMPL):
    def __init__(self, model_path, gender="neutral"):
        super().__init__(
            model_path=osp.join(model_path, "smpl"),
            gender=gender,
            create_betas=False,
            create_body_pose=False,
            create_global_orient=False,
            create_transl=False,
            use_hands=False,
            use_feet_keypoints=False,
        )


class SMPL(nn.Module):
    def __init__(
        self,
        model_path,
    ):
        super().__init__()

        self._smpl_dict = nn.ModuleDict(
            {
                "neutral": BaseSMPL(model_path, gender="neutral"),
                "male": BaseSMPL(model_path, gender="male"),
                "female": BaseSMPL(model_path, gender="female"),
            }
        )
        self.faces = self._smpl_dict["neutral"].faces

        J_regressor_extra = torch.from_numpy(
            np.load(osp.join(model_path, "J_regressor_extra.npy"))
        ).float()
        self.register_buffer("J_regressor_extra", J_regressor_extra)

        J_regressor_h36m_correct = torch.from_numpy(
            np.load(osp.join(model_path, "J_regressor_h36m_correct.npy"))
        ).float()
        self.register_buffer("J_regressor_h36m_correct", J_regressor_h36m_correct)

    def forward(self, betas, pose, gender="neutral", return_dict=False):
        gender = gender.lower()
        if gender == "f":
            gender = "female"
        elif gender == "m":
            gender = "male"

        output = self._smpl_dict[gender](
            betas, body_pose=pose[:, 3:], global_orient=pose[:, :3]
        )
        # vertices = output["vertices"]
        # joints = output["joints"]
        if return_dict:
            return output
        return output["vertices"]

    def get_h36m_joints(self, vertices):
        """h36m: 17 joints"""
        return vertices2joints(self.J_regressor_h36m_correct, vertices)

    def get_joints(self, vertices, gender="neutral"):
        """get 24 joints"""
        gender = gender.lower()
        if gender == "f":
            gender = "female"
        elif gender == "m":
            gender = "male"

        joints = vertices2joints(self._smpl_dict[gender].J_regressor, vertices)
        joints_extra = vertices2joints(self.J_regressor_extra, vertices)
        # 38 joints
        joints = torch.cat((joints, joints_extra), dim=1)
        # 24 joints
        joints = joints[:, SMPL_J24]
        return joints
