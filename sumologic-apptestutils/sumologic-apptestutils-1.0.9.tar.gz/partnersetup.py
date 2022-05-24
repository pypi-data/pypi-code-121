from setuptools import setup, find_packages
from os.path import join, dirname, abspath
import io

here = abspath(dirname(__file__))


def get_version(rel_path):
    with open(join(here, rel_path), 'r') as fp:
        version_content = fp.read()
        for line in version_content.splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")

__versionstr__ = get_version("sumoapputils/partner/__init__.py")

with open(join(here, 'requirements.txt')) as REQUIREMENTS:
    INSTALL_REQUIRES = REQUIREMENTS.read().split('\n')


with io.open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


CONSOLE_SCRIPTS = [
    'sumoapp=sumoapputils.partner.console:apputilscli'
]


setup(
    name="sumologic-apptestutils",
    version=__versionstr__,
    packages=find_packages(exclude=["sumoapputils.appdev"]),
    install_requires=INSTALL_REQUIRES,
    extras_require={
        'dev': ["twine", "wheel", "setuptools", "check-manifest"]
    },
    # PyPI metadata
    author="SumoLogic",
    author_email="it@sumologic.com, apps-team@sumologic.com",
    description="SumoLogic app testing utitities",
    license="PSF",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="sumologic python rest api log management analytics sumoapptestutils test agent",
    url="https://github.com/SumoLogic/sumologic-partner-utils",
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console_scripts': CONSOLE_SCRIPTS,
    }

)
