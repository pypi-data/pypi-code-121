import sys

from setuptools import setup


# This appears to be necessary so that versioneer works:
sys.path.insert(0, ".")
import versioneer  # pylint: disable=wrong-import-position


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
