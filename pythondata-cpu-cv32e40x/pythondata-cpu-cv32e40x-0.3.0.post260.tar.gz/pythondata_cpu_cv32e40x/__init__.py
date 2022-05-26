import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.3.0.post260"
version_tuple = (0, 3, 0, 260)
try:
    from packaging.version import Version as V
    pversion = V("0.3.0.post260")
except ImportError:
    pass

# Data version info
data_version_str = "0.3.0.post124"
data_version_tuple = (0, 3, 0, 124)
try:
    from packaging.version import Version as V
    pdata_version = V("0.3.0.post124")
except ImportError:
    pass
data_git_hash = "285a5ad2baadd44a7c552c54060164c4cb6197ef"
data_git_describe = "0.3.0-124-g285a5ad2"
data_git_msg = """\
commit 285a5ad2baadd44a7c552c54060164c4cb6197ef
Merge: ac753589 e4efbdd2
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Tue May 24 11:55:27 2022 +0200

    Merge pull request #551 from silabs-oysteink/silabs-oysteink_wb-valid-last
    
    wb_valid for all suboperations

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
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn
