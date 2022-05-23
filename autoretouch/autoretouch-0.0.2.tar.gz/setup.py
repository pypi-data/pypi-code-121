import os
from subprocess import run

from setuptools import setup, find_packages
from setuptools.command.install import install


def add_autocompletion():
    try:
        config_root = os.path.join(os.path.expanduser("~"), ".config", "autoretouch")
        os.makedirs(config_root, exist_ok=True)
    except Exception as e:
        print(f"failed to install autocompletion. Exception was: {str(e)}")

    def add_bash():
        run(f"cp autoretouch/.autoretouch-complete.sh {config_root}/".split())
        bashrc_path = os.path.expanduser("~/.bashrc")
        if os.path.isfile(bashrc_path):
            string_to_add = "\n\n# autoretouch auto-completion\n. ~/.config/autoretouch/.autoretouch-complete.sh\n\n"
            with open(bashrc_path, "r") as f:
                bashrc_has_been_added = string_to_add in f.read()
            if not bashrc_has_been_added:
                os.system(f"echo \"{string_to_add}\" >> {bashrc_path}")

    def add_fish():
        run(f"cp autoretouch/.autoretouch-complete.fish {config_root}/".split())
        fish_completions_path = os.path.expanduser("~/.config/fish/completions")
        if os.path.isdir(fish_completions_path):
            fish_completion_file_path = os.path.join(fish_completions_path, ".autoretouch-complete.fish")
            if not os.path.isfile(fish_completion_file_path):
                os.system(f"cp autoretouch/.autoretouch-complete.fish {fish_completion_file_path}")

    def add_zsh():
        run(f"cp autoretouch/.autoretouch-complete.zsh {config_root}/".split())
        zshrc_path = os.path.expanduser("~/.zshrc")
        if os.path.isfile(zshrc_path):
            string_to_add = "\n\n# autoretouch auto-completion\n. ~/.config/autoretouch/.autoretouch-complete.zsh\n\n"
            with open(zshrc_path, "r") as f:
                zshrc_has_been_added = string_to_add in f.read()
            if not zshrc_has_been_added:
                os.system(f"echo \"{string_to_add}\" >> {zshrc_path}")

    def add_powershell():
        pass

    for shell, shell_func in {
        "bash": add_bash, "fish": add_fish, "zsh": add_zsh, "powershell": add_powershell
    }.items():
        try:
            print(f"add autocompletion for {shell}")
            shell_func()
        except Exception as e:
            print(f"failed to install autocompletion for {shell}. Exception was: {str(e)}")


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    # TODO
    #  - autocomplete fish, powershell
    def run(self):
        install.run(self)
        add_autocompletion()


with open("README.md", "r") as f:
    README = f.read()

setup(
    name="autoretouch",
    version="0.0.2",
    author=[
        "Antoine Daurat <antoine@autoretouch.com>",
        "Oliver Allweyer <oliver@autoretouch.com>",
        "Till Lorentzen <till@autoretouch.com>"
    ],
    description="cli and python package to communicate with the autoRetouch API",
    long_description=README,
    long_description_content_type="text/markdown",
    license="BSD Zero",
    packages=find_packages(exclude=["test", "assets", "tmp"]),
    install_requires=[
        "requests",
        "click==8.1.3",
        "click-log==0.4.0"
    ],
    extra_requires={
        "test": [
            "assertpy"
        ],
    },
    include_package_data=True,
    package_data={
        "autoretouch": [".autoretouch-complete.zsh", ".autoretouch-complete.bash", ".autoretouch-complete.fish"]
    },
    entry_points={
        "console_scripts": [
            "autoretouch = autoretouch.cli.commands:autoretouch_cli",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostInstallCommand
    },
)
