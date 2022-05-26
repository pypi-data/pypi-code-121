import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "sources")
src = "https://github.com/lambdaconcept/minerva"

# Module version
version_str = "0.0.post256"
version_tuple = (0, 0, 256)
try:
    from packaging.version import Version as V
    pversion = V("0.0.post256")
except ImportError:
    pass

# Data version info
data_version_str = "0.0.post120"
data_version_tuple = (0, 0, 120)
try:
    from packaging.version import Version as V
    pdata_version = V("0.0.post120")
except ImportError:
    pass
data_git_hash = "08251daae42ec8cfc54fb82865a5942727186192"
data_git_describe = "v0.0-120-g08251da"
data_git_msg = """\
commit 08251daae42ec8cfc54fb82865a5942727186192
Author: Jean-François Nguyen <jf@jfng.fr>
Date:   Tue Apr 5 15:33:21 2022 +0200

    stage: fix commit 6c3294b9.

"""

# Tool version info
tool_version_str = "0.0.post136"
tool_version_tuple = (0, 0, 136)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post136")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_minerva."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_minerva".format(f))
    return fn
