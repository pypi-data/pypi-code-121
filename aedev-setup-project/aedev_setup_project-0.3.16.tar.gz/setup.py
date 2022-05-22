# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.tpl_project V0.3.17
""" setup this project with setuptools and aedev.setup_project. """
import pprint
import sys

import setuptools

from aedev.setup_project import project_env_vars    # type: ignore

pev = project_env_vars(from_setup=True)

if __name__ == "__main__":
    print("#  EXECUTING SETUPTOOLS SETUP: argv, kwargs  ###################")
    print(pprint.pformat(sys.argv, indent=3, width=75, compact=True))
    setup_kwargs = pev['setup_kwargs']
    print(pprint.pformat(setup_kwargs, indent=3, width=75, compact=True))
    setuptools.setup(**setup_kwargs)
    print("#  FINISHED SETUPTOOLS SETUP  ##################################")
