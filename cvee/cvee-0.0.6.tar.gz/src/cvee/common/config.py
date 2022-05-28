import os

import yaml
from yacs.config import CfgNode as _CfgNode

import cvee

BASE_KEY = "_BASE_"


class CfgNode(_CfgNode):
    """
    Ref: https://github.com/facebookresearch/fvcore/blob/main/fvcore/common/config.py
    """

    @classmethod
    def load_yaml_with_base(cls, filename, allow_unsafe=True):
        """
        Just like `yaml.load(open(filename))`, but inherit attributes from its `_BASE_`.

        Args:
            filename (str or file-like object): the file name or file of the current config.
                Will be used to find the base config file.
            allow_unsafe (bool): whether to allow loading the config file with `yaml.unsafe_load`.

        Returns:
            (dict): the loaded yaml
        """
        with open(filename, "r") as f:
            try:
                cfg = yaml.safe_load(f)
            except yaml.constructor.ConstructorError:
                if not allow_unsafe:
                    raise
                logger = cvee.get_logger(__name__)
                logger.warning(
                    "Loading config {} with yaml.unsafe_load. Your machine may "
                    "be at risk if the file contains malicious content.".format(filename)
                )
                f.close()
                with cls._open_cfg(filename) as f:
                    cfg = yaml.unsafe_load(f)

        def merge_a_into_b(a, b):
            # merge dict a into dict b. values in a will overwrite b.
            for k, v in a.items():
                if isinstance(v, dict) and k in b:
                    assert isinstance(b[k], dict), "Cannot inherit key '{}' from base!".format(k)
                    merge_a_into_b(v, b[k])
                else:
                    b[k] = v

        def _load_with_base(base_cfg_file):
            if base_cfg_file.startswith("~"):
                base_cfg_file = os.path.expanduser(base_cfg_file)
            if not any(map(base_cfg_file.startswith, ["/", "https://", "http://"])):
                # the path to base cfg is relative to the config file itself.
                base_cfg_file = os.path.join(os.path.dirname(filename), base_cfg_file)
            return cls.load_yaml_with_base(base_cfg_file, allow_unsafe=allow_unsafe)

        if BASE_KEY in cfg:
            if isinstance(cfg[BASE_KEY], list):
                base_cfg = {}
                base_cfg_files = cfg[BASE_KEY]
                for base_cfg_file in base_cfg_files:
                    merge_a_into_b(_load_with_base(base_cfg_file), base_cfg)
            else:
                base_cfg_file = cfg[BASE_KEY]
                base_cfg = _load_with_base(base_cfg_file)
            del cfg[BASE_KEY]

            merge_a_into_b(cfg, base_cfg)
            return base_cfg
        return cfg

    def merge_from_file(self, cfg_filename, allow_unsafe=True) -> None:
        """
        Merge configs from a given yaml file.

        Args:
            cfg_filename: the file name of the yaml config.
            allow_unsafe: whether to allow loading the config file with
                `yaml.unsafe_load`.
        """
        loaded_cfg = self.load_yaml_with_base(cfg_filename, allow_unsafe=allow_unsafe)
        loaded_cfg = type(self)(loaded_cfg)
        self.merge_from_other_cfg(loaded_cfg)

    # Forward the following calls to base, but with a check on the BASE_KEY.
    def merge_from_other_cfg(self, cfg_other):
        """
        Args:
            cfg_other (CfgNode): configs to merge from.
        """
        assert BASE_KEY not in cfg_other, "The reserved key '{}' can only be used in files!".format(BASE_KEY)
        return super().merge_from_other_cfg(cfg_other)

    def merge_from_list(self, cfg_list):
        """
        Args:
            cfg_list (list): list of configs to merge from.
        """
        keys = set(cfg_list[0::2])
        assert BASE_KEY not in keys, "The reserved key '{}' can only be used in files!".format(BASE_KEY)
        return super().merge_from_list(cfg_list)
