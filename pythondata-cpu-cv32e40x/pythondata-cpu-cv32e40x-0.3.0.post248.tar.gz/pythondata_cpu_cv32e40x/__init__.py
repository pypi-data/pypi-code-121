import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.3.0.post248"
version_tuple = (0, 3, 0, 248)
try:
    from packaging.version import Version as V
    pversion = V("0.3.0.post248")
except ImportError:
    pass

# Data version info
data_version_str = "0.3.0.post120"
data_version_tuple = (0, 3, 0, 120)
try:
    from packaging.version import Version as V
    pdata_version = V("0.3.0.post120")
except ImportError:
    pass
data_git_hash = "ac7535894b072a4ec988b66d5c7d5a7987101a52"
data_git_describe = "0.3.0-120-gac753589"
data_git_msg = """\
commit ac7535894b072a4ec988b66d5c7d5a7987101a52
Merge: b1602721 c5985939
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Tue May 24 07:45:23 2022 +0200

    Merge pull request #550 from Silabs-ArjanB/ArjanB_549
    
    Fixed mcause reset value for SMCLIC=1 configuration

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
