import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.3.0.post277"
version_tuple = (0, 3, 0, 277)
try:
    from packaging.version import Version as V
    pversion = V("0.3.0.post277")
except ImportError:
    pass

# Data version info
data_version_str = "0.3.0.post137"
data_version_tuple = (0, 3, 0, 137)
try:
    from packaging.version import Version as V
    pdata_version = V("0.3.0.post137")
except ImportError:
    pass
data_git_hash = "3a3aecea53f0944e6d84b0eff165740becd018a6"
data_git_describe = "0.3.0-137-g3a3aecea"
data_git_msg = """\
commit 3a3aecea53f0944e6d84b0eff165740becd018a6
Merge: d0e922da bdffac6d
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Fri May 27 08:53:57 2022 +0200

    Merge pull request #552 from silabs-oysteink/silabs-oysteink_zc-tbl-1
    
    Zc* table jumps

"""

# Tool version info
tool_version_str = "0.0.post140"
tool_version_tuple = (0, 0, 140)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post140")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn
