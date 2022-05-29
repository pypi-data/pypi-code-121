import importlib
import os.path as osp
import shutil

from omegaconf import OmegaConf

from ..tools.logger import Logger


def get_obj_from_str(string, reload=False):
    module, cls = string.rsplit(".", 1)
    if reload:
        module_imp = importlib.import_module(module)
        importlib.reload(module_imp)
    return getattr(importlib.import_module(module, package=None), cls)


def instantiate_from_config(config):
    if not "target" in config:
        raise KeyError("Expected key `target` to instantiate.")
    return get_obj_from_str(config["target"])(**config.get("params", dict()))


def load_config(filename):
    """加载参数文件"""

    filename = osp.abspath(filename)
    config = OmegaConf.load(filename)

    Logger.info(f"load_config: {filename}")
    # merge config
    if hasattr(config, "base"):
        base_filename = osp.join(osp.dirname(filename), config.base)
        delattr(config, "base")

        base_config = load_config(base_filename)
        config = OmegaConf.merge(base_config, config)
    return config


def save_config(filename, config):
    OmegaConf.save(config, filename)
    Logger.info(f"save_config: {filename}")


def make_config():
    src = osp.join(osp.dirname(__file__), "template.yaml")
    dst = "template.yaml"
    shutil.copy(src, dst)
    Logger.info(f"create: {dst}")


def get_log_dir(config_filename):
    return config_filename.replace("configs", "logs").replace(".yaml", "")


def omegaconf_to_dict(cfg):
    d = dict()
    for key, value in cfg.items():
        d[key] = value
    return d
