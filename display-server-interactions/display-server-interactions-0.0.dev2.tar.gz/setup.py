from setuptools import setup, find_packages
from os.path import dirname, join, abspath
# def read_requirements(file):
#    with open(file) as f:
#        return f.read().splitlines()


def read(rel_path: str) -> str:
    here = abspath(dirname(__file__))
    with open(join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


#requirements = read_requirements("requirements.txt")

def main() -> None:
    setup(
        name="display-server-interactions",
        version=get_version("display_server_interactions/__init__.py"),

        author="Commandcracker",

        # url="https://github.com/Commandcracker/display-server-interactions",

        project_urls={
            "Documentation": "https://display-server-interactions.readthedocs.io/en/latest/",
            "Source": "https://github.com/Commandcracker/display-server-interactions",
            "Tracker": "https://github.com/Commandcracker/display-server-interactions/issues"
        },

        description="DSI allows you to perform basic interactions on your display server, like screenshotting a window or sending input to it.",
        long_description_content_type="text/markdown",
        long_description=read("README.md"),

        py_modules=["display_server_interactions"],

        keywords=[
            "screen",
            "display",
            "screenshot",
            "input",
            "window",
            "screencapture",
            "screengrab",
        ],

        license="Apache Software License",
        packages=find_packages(exclude=["test"]),
        # install_requires=requirements,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",

            "License :: OSI Approved :: Apache Software License",

            "Operating System :: POSIX :: Linux",
            #"Operating System :: OS Independent",

            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",

            "Topic :: Multimedia :: Graphics",
            "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        ]
    )


if __name__ == "__main__":
    main()
