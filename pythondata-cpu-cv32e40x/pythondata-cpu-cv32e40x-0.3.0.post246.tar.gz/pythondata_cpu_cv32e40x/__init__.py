import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.3.0.post246"
version_tuple = (0, 3, 0, 246)
try:
    from packaging.version import Version as V
    pversion = V("0.3.0.post246")
except ImportError:
    pass

# Data version info
data_version_str = "0.3.0.post118"
data_version_tuple = (0, 3, 0, 118)
try:
    from packaging.version import Version as V
    pdata_version = V("0.3.0.post118")
except ImportError:
    pass
data_git_hash = "b160272140cf79c80ff85dfb7412ced8361e7863"
data_git_describe = "0.3.0-118-gb1602721"
data_git_msg = """\
commit b160272140cf79c80ff85dfb7412ced8361e7863
Merge: 90e95bd9 c2b13bbb
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Mon May 23 08:56:57 2022 +0200

    Merge pull request #548 from silabs-oysteink/silabs-oysteink_clic-data-remove-1
    
    Further removal of CLIC pointers using data access.

"""

# Tool version info
tool_version_str = "0.0.post128"
tool_version_tuple = (0, 0, 128)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post128")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn
