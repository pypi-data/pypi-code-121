from dist_meta.core import DistInfo
import sys

# [python scripts]
def gen_distinfo_py(distribution: str, path: str):
    """
    Generates a dist info yaml file from a distribution name installed in the running environment
    :param distribution: Name of the distribution
    :param path: Path to the output yaml file (full path, absolute)
    """
    dist_info = DistInfo.from_env(distribution)
    dist_info.to_yaml(path)


# [console scripts]
def gen_distinfo_cmd():
    """
    Generates a dist info yaml file from a distribution name installed in the running environment
    Takes argugments (distribution:str, path:str) from the command
    :param distribution: Name of the distribution
    :param path: Path to the output yaml file (full path, absolute)
    """
    distribution = sys.argv[1]
    path = sys.argv[2]
    gen_distinfo_py(distribution, path)
