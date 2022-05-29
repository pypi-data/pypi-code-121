import os
import os.path as osp

import torch

from .config import get_log_dir, instantiate_from_config, load_config

__all__ = ["load_checkpoint", "get_best_checkpoint", "get_model"]


def load_checkpoint(model, checkpoint_file):
    state_dict = torch.load(checkpoint_file)["state_dict"]
    new_state_dict = dict()
    for key, value in state_dict.items():
        new_state_dict[key[len("model.") :]] = value
    model.load_state_dict(new_state_dict)
    return model


def get_best_checkpoint_from_folder(folder, select="min"):
    """获取最好的模型文件
    select: min, max
    """
    assert select in ["min", "max"]

    name_list = os.listdir(folder)
    if "last.ckpt" in name_list:
        name_list.remove("last.ckpt")

    best_score = None
    best_name = None
    for name in name_list:
        score = float(name.split("=")[-1].replace(".ckpt", ""))
        if best_score is None:
            best_score, best_name = score, name

        if select == "min" and score < best_score:
            best_score, best_name = score, name
        elif select == "max" and score > best_score:
            best_score, best_name = score, name

    if best_name is None:
        return None

    return osp.join(folder, best_name)


def get_best_checkpoint(config_filename, select="min"):
    checkpoint_folder = osp.join(get_log_dir(config_filename), "checkpoint")
    return get_best_checkpoint_from_folder(checkpoint_folder, select=select)


def get_model(config_filename):
    config = load_config(config_filename)
    model = instantiate_from_config(config.model)
    return model
