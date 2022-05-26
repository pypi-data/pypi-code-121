import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "verilog")
src = "https://github.com/openrisc/mor1kx.git"

# Module version
version_str = "5.1.1.post136"
version_tuple = (5, 1, 1, 136)
try:
    from packaging.version import Version as V
    pversion = V("5.1.1.post136")
except ImportError:
    pass

# Data version info
data_version_str = "5.1.1.post0"
data_version_tuple = (5, 1, 1, 0)
try:
    from packaging.version import Version as V
    pdata_version = V("5.1.1.post0")
except ImportError:
    pass
data_git_hash = "4cebbb684bba8f9fe74f9b69e679796d4fd4a35b"
data_git_describe = "v5.1.1-0-g4cebbb6"
data_git_msg = """\
commit 4cebbb684bba8f9fe74f9b69e679796d4fd4a35b
Merge: 44ea698 1a8c19b
Author: Stafford Horne <shorne@gmail.com>
Date:   Mon May 23 06:01:28 2022 +0900

    Merge pull request #147 from stffrdhrn/or1k-linux-failing
    
    Revert "dcache: Allow writing during write_pending"

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
    """Get absolute path for file inside pythondata_cpu_mor1kx."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_mor1kx".format(f))
    return fn
