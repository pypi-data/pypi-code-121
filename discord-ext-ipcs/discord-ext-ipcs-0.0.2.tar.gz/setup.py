import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def _requires_from_file(filename):
    return open(filename, encoding="utf8").read().splitlines()


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
    version="0.0.2",
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
