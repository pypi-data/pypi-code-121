import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.3.0.post282"
version_tuple = (0, 3, 0, 282)
try:
    from packaging.version import Version as V
    pversion = V("0.3.0.post282")
except ImportError:
    pass

# Data version info
data_version_str = "0.3.0.post142"
data_version_tuple = (0, 3, 0, 142)
try:
    from packaging.version import Version as V
    pdata_version = V("0.3.0.post142")
except ImportError:
    pass
data_git_hash = "c27b73db52f54bab836a91d157115d85122640ec"
data_git_describe = "0.3.0-142-gc27b73db"
data_git_msg = """\
commit c27b73db52f54bab836a91d157115d85122640ec
Merge: 66b8050d 075f9a34
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Fri May 27 15:43:57 2022 +0200

    Merge pull request #555 from Silabs-ArjanB/ArjanB_549
    
    Fix for issue #549. Clean up CS registers syntax. Tie RVFI to RTL ins…

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
