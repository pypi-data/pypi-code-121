import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "verilog")
src = "https://github.com/openrisc/or1k_marocchino.git"

# Module version
version_str = "0.0.post203"
version_tuple = (0, 0, 203)
try:
    from packaging.version import Version as V
    pversion = V("0.0.post203")
except ImportError:
    pass

# Data version info
data_version_str = "0.0.post67"
data_version_tuple = (0, 0, 67)
try:
    from packaging.version import Version as V
    pdata_version = V("0.0.post67")
except ImportError:
    pass
data_git_hash = "6e010fd5b1da54632939052e7007c9c412aae6bb"
data_git_describe = "v0.0-67-g6e010fd"
data_git_msg = """\
commit 6e010fd5b1da54632939052e7007c9c412aae6bb
Author: Andrey Bacherov <bandvig@mail.ru>
Date:   Wed Feb 9 10:52:12 2022 +0300

    Final fix I(D)MMUs super-cache miss detection. Plus some re-factoring.

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
    """Get absolute path for file inside pythondata_cpu_marocchino."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_marocchino".format(f))
    return fn
