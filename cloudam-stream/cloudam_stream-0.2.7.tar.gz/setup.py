from distutils.core import setup
from setuptools import find_packages

try:
# for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.network.session import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.requirement) for ir in install_reqs]

setup(
    name="cloudam_stream",
    version="0.2.7",
    packages=find_packages("cloudam"),
    package_dir={'': 'cloudam'},
    exclude_package_data={'': ['README.md'], 'tests': ['*.py']},
    install_requires=reqs,
    python_requires='>=3.6'
)