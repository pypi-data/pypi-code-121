from pathlib import Path

from setuptools import setup

PROJDIR = Path(__file__).resolve().parent
README = (PROJDIR / "README.md").read_text()

setup(
    name="tcr-roboclaw",
    version="0.0.1",
    description="An easy to install version of BasicMicro's Roboclaw Python library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/team-chat-robotique/libraries/team-chat-robotique-roboclaw-python",
    author="damienlarocque",
    author_email="phicoltan@gmail.com",
    packages=["tcr_roboclaw"],
    install_requires=["pyserial"],
)
