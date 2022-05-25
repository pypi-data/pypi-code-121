import os
import re
import setuptools

with open("README.MD", "r") as fh:
    long_description = fh.read()


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\s*=\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


projectname = find_projectname()
file = os.path.join(projectname, "__init__.py")
version = find_version(file)


setuptools.setup(
    name="pttydev",
    version=version,
    author="k.r. goger",
    author_email="k.r.goger+{projectname}@gmail.com",
    description="TTYDev - Pseudo TTY Device",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kr-g/pttydev",
    packages=setuptools.find_packages(),
    license="MIT",
    keywords="python threading pyserial websocket websocket-client micropython webrepl esp8266 esp32",
    install_requires=[
        "pyatomic==0.0.2",
        "pyserial",
        "websocket-client",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
