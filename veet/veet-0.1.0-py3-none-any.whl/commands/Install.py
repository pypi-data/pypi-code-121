from veet.commands import veet
from subprocess import call
import os


if os.path.isfile('requirements.txt'):
    @veet.command(name="install")
    def handle():
        """
        Install all of requirements.txt
        """
        try:
            call(["pip", "install", "-r", "requirements.txt"])
        except Exception:
            call(["pip3", "install", "-r", "requirements.txt"])