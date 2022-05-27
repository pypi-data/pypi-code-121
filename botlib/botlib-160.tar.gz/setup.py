# This file is placed in the Public Domain.


from setuptools import setup


def read():
    return open("README.rst", "r").read()


setup(
    name="botlib",
    version="160",
    url="https://github.com/bthate/botlib",
    author="Bart Thate",
    author_email="bthate67@gmail.com",
    description="the python3 bot namespace.",
    long_description=read(),
    license="Public Domain",
    packages=["bot", "bot.cmd"],
    scripts=["bin/bot", "bin/botcmd", "bin/botctl", "bin/botd"],
    include_package_data=True,
    data_files=[
                ("share/botd", ("files/botd.service",)),
               ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)
