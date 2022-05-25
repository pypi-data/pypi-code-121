import json
import os
from typing import Dict

from notebook.base.handlers import APIHandler


class Environment_handler(APIHandler):
    """
    Environment Handler.  Return the JSON representation of our OS environment
    settings.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = {}
        self._refresh_env()

    def get(self) -> None:
        """ """
        self.log.info("Sending Rubin settings")
        self.finish(self.dump())

    def dump(self) -> str:
        self._refresh_env()
        return json.dumps(self.env, sort_keys=True, indent=4)

    def _refresh_env(self) -> None:
        # This is a little complex.  Some of the environment comes in as
        #  a ConfigMap.  This *could* be updated while we're running
        #  (and, for instance, maybe will be for token updates).  But the
        #  running process won't see those updates--it will have the
        #  environment it was started from.  We want to return the environment
        #  reflecting any updates to the ConfigMap.
        #
        # So we keep track of our own environment, and construct that from
        #  the OS environment but also by overriding any values with what
        #  we find where our environmental configmap is mounted.
        #
        loc = "/opt/lsst/software/jupyterlab/environment"  # By convention.
        fns = os.listdir(path=loc)
        ev = {}
        for fn in fns:
            if fn.startswith(".."):
                # This is a configmap implementation detail--..data points to
                #  the current configmap, ..<date> points to various revisions,
                #  and the files are symlinked to ..data/filename
                continue
            with open(os.path.join(loc, fn), "r") as f:
                ev[fn] = f.read()
        ev.update(self._env_to_dict())
        self.env.update(ev)

    def _env_to_dict(self) -> Dict[str, str]:
        ev = {}
        for var in os.environ:
            ev[var] = os.environ[var]
        return ev
