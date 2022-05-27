import os

import setuptools

current_path = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_file(path_segments):
    """Read a file from the package. Takes a list of strings to join to
    make the path"""
    file_path = os.path.join(current_path, *path_segments)
    with open(file_path) as f:
        return f.read()


def exec_file(path_segments):
    """Execute a single python file to get the variables defined in it"""
    result = {}
    code = read_file(path_segments)
    exec(code, result)
    return result


version = exec_file(("chaanbot", "__init__.py"))["__version__"]

setuptools.setup(
    name="chaanbot",
    version=version,
    author="Richard Nysäter",
    author_email="richard@nysater.org",
    description="A Matrix chat bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3+",
    url="https://github.com/RichardNysater/chaanbot",
    packages=setuptools.find_packages(exclude=["chaanbot.modules.private"]),
    install_requires=["matrix-nio", "appdirs", "requests"],
    package_data={'': ['chaanbot.cfg.sample']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Communications :: Chat",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    keywords="matrix chat bot",
    python_requires=">=3.5",
    entry_points={
        'console_scripts': [
            'chaanbot=chaanbot.start:main',
        ],
    },
    test_suite="tests",
)
