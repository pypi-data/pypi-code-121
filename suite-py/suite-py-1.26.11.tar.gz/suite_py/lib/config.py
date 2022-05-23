# -*- encoding: utf-8 -*-
import json
import os

import yaml

from suite_py.lib import logger


class Config:
    def __init__(self, home_path=os.environ["HOME"]):
        self.user = {}
        self.youtrack = {}
        self.vault = {}
        self.aws = {}
        self._config_path_file = os.path.join(home_path, ".suite_py/config.yml")
        self._base_cache_path = os.path.join(home_path, ".suite_py/cache")

        if not os.path.exists(self._base_cache_path):
            os.makedirs(self._base_cache_path)
        self._load()

    def _load(self):
        with open(self._config_path_file, encoding="utf-8") as configfile:
            conf = yaml.safe_load(configfile)

        conf["user"]["projects_home"] = os.path.join(
            os.environ["HOME"], conf["user"]["projects_home"]
        )

        conf["user"].setdefault("review_channel", "#review")
        conf["user"].setdefault("deploy_channel", "#deploy")
        conf["user"].setdefault("default_slug", "PRIMA-XXX")
        conf["user"].setdefault("captainhook_timeout", 30)  # This is in seconds
        conf["user"].setdefault(
            "captainhook_url", "http://captainhook-internal.prima.it"
        )
        conf["user"].setdefault("use_commits_in_pr_body", False)
        conf["user"].setdefault("delete_qa_after_merge", True)

        _load_local_config(conf)

        for k, v in conf.items():
            setattr(self, k, v)

        # AWS section
        try:
            self.aws = conf["aws"]
        except KeyError:
            pass

    def put_cache(self, key, data):
        with open(
            os.path.join(self._base_cache_path, key), "w", encoding="utf-8"
        ) as cache_file:
            json.dump(data, cache_file)

    def get_cache(self, key):
        try:
            with open(
                os.path.join(self._base_cache_path, key), encoding="utf-8"
            ) as cache_file:
                return json.load(cache_file)
        except Exception:
            logger.error(
                f"I couldn't find any cached version for the key {key}. Turn on the VPN."
            )
            return ""
            # sys.exit(-1)


def _load_local_config(conf):
    local_conf_path = os.path.join(os.curdir, ".suite_py.yml")
    try:
        with open(local_conf_path, encoding="utf-8") as f:
            local_conf = yaml.safe_load(f)

            for key in conf.keys():
                conf[key].update(local_conf.get(key, {}))

    except FileNotFoundError:
        pass
