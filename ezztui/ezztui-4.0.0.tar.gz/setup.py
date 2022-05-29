from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ezztui",
    version="4.0.0",
    py_modules=["ezztui"],
    author="BarsTiger",
    description="Easy TextUI creating package",
    long_description=long_description,
    license='MIT',
    url='https://github.com/BarsTiger/ezztui',
    long_description_content_type="text/markdown",
    keywords=["textui", "curses", "tui", "autotui", "autoui", "autogui", "crossplatform"]
)
