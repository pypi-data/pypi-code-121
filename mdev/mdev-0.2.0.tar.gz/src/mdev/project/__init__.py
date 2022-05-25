# Author: Snow Yang
# Date  : 2022/03/28

"""Creation and management of Mxos OS projects.

* Creation of a new Mxos OS application.
* Cloning of an existing Mxos OS program.
* Deploy of a specific version of Mxos OS or library.
"""

from mdev.project.project import initialise_project, import_project, deploy_project, sync_project, get_known_libs
from mdev.project.mxos_program import MxosProgram
