from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# this grabs the requirements from requirements.txt
install_requires = [i.strip() for i in open("requirements.txt").readlines()]

VERSION = '0.8.2'
DESCRIPTION = 'Tasks/jobs/rules engine, primarily intended for use in a smarthome environment.'

# Setting up
setup(
    author="Rosenloecher-IT (Raul Rosenlöcher)",
    author_email="<github@rosenloecher-it.de>",
    description=DESCRIPTION,
    install_requires=install_requires,
    keywords=['smarthome', 'mqtt', 'rule-engine', 'task-engine'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="worker-bunch",
    packages=find_packages(),
    url='https://github.com/rosenloecher-it/worker-bunch',
    version=VERSION,
    classifiers=[  # https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
    ]
)
