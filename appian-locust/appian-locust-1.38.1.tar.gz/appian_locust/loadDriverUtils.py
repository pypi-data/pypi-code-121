import json
import os
from . import logger

default_config = {
    "host_address": "replace-me.host.net",
    "cluster_size": 1,
    "tests": "all",
    "run_time_in_secs": 300,
    "num_concur_users": 8,
    "hatch_rate_per_sec": 4,
    # Specify task weights here:
    "task_weights": {
        "exec_java_task": 1,
        "exec_k_task": 1,
        "exec_java_k_task": 1,
        "exec_start_end_task": 1,
    },
    "skip_machine_setup": False,
    "auth": ["username", "password"]
}

log = logger.getLogger(__name__)


class loadDriverUtils:
    def __init__(self) -> None:
        self.c = default_config

    def load_config(self, config_file: str = "./config.json") -> dict:
        if os.path.exists(config_file):
            self.c = json.load(open(config_file))
            return self.c
        else:
            log.error("Failed to load config ({}), exiting.".format(config_file))
            log.error("Example config:{}".format(json.dumps(default_config,
                                                            indent=2)))
            exit(1)


utils = loadDriverUtils()

# Aliased for backwards compatability
utls = utils
