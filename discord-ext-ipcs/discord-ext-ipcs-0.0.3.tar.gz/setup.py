import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def _requires_from_file(filename):
    return open(filename, encoding="utf8").read().splitlines()

def _get_version(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    version = None
    for line in lines:
        if "__version__" in line:
            version = line.split()[2]
            break
    return version.replace('"', '')


extras_require = {
    "speed": [
        "orjson"
    ]
}

packages = [
    "discord.ext.ipcs"
]

setuptools.setup(
    name="discord-ext-ipcs",
    version=_get_version("discord/ext/ipcs/__init__.py"),
    author="DMS",
    author_email="masato190411@gmail.com",
    description="Discord ipc client.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuna2134/discord-ext-ipcs",
    install_requires=_requires_from_file('requirements.txt'),
    extras_require=extras_require,
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
