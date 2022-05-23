from abc import ABC, abstractmethod
import os
import shutil
import pathlib
from dotpyle.services.repo_handler import RepoHandler
from dotpyle.services.logger import Logger
from dotpyle.decorators.pass_repo_handler import pass_repo_handler
from dotpyle.objects.base import PathLike, ShellCommand
#from dotpyle.objects.profile import Profile # circular import


class BaseAction(ABC):
    @abstractmethod
    def run(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...


class LinkAction(BaseAction):
    def __init__(self, source: PathLike, link_name: PathLike):
        self.source = source
        self.link_name = link_name

    def __str__(self) -> str:
        return "[Link action]: link {} to {}".format(self.source,
                                                     self.link_name)

    def run(self):
        os.symlink(src=self.source, dst=self.link_name)
        print("Linking {} -> {}".format(self.source, self.link_name))

    def rollback(self):
        os.unlink(self.link_name)
        print("LinkAction rollback: Unlink {}".format(self.link_name))


class UnlinkAction(BaseAction):
    def __init__(self, link_name: PathLike):
        self.link_name = link_name

    def __str__(self) -> str:
        return "[Unlink action]: unlink {}".format(self.link_name)

    def run(self):
        self.source = os.readlink(self.link_name)
        os.unlink(self.link_name)
        print("Unlinking {}".format(self.link_name))

    def rollback(self):
        os.symlink(src=self.source, dst=self.link_name)
        print("Rollback: Linking {} -> {}".format(self.source, self.link_name))


class ScriptAction(BaseAction):
    def __init__(self, commands: list[ShellCommand]):
        self.commands = commands

    def __str__(self) -> str:
        return "[Script action]: commands:\n {}".format(self.commands)

    def run(self):
        print("Execute...\n {}".format(self.commands))

    def rollback(self):
        pass


class RepoAction(BaseAction):
    import click

    def __init__(self,
                 profile):  # TODO cannot type Profile (circular dependency)
        self.profile = profile

    def __str__(self) -> str:
        return "[Repo action]: "

    # @pass_repo_handler
    #@click.pass_context
    def run(self):
        #from dotpyle.utils.constants import REPO_HANDLER_PROVIDER
        #repo_handler = ctx.meta[REPO_HANDLER_PROVIDER]
        repo_handler = RepoHandler(
            Logger(verbose=True))  # TODO inject dependency
        commit_message = "[Dotpyle]: added {} profile for {} ".format(
            self.profile.profile_name, self.profile.dotfile_name)

        print(commit_message)
        repo_handler.add(self.profile.get_repo_paths(),
                         config_file_changed=True)
        repo_handler.commit(commit_message)
        print("Added paths: {}, of profile {} on program {}".format(
            self.profile.paths, self.profile.profile_name,
            self.profile._dotfile_name))

    def rollback(self):
        pass


class MoveAction(BaseAction):
    def __init__(self, source_path, dest_path):
        self.source_path = source_path
        self.dest_path = dest_path

    def __str__(self) -> str:
        return "[Move action]: {} -> {}".format(self.source_path,
                                                self.dest_path)

    def run(self):
        if os.path.isdir(self.source_path):
            print("Moving a folder")
        else:
            print("Moving a file")

        # Create path if not exist
        pathlib.Path(str(os.path.dirname(self.dest_path))).mkdir(parents=True,
                                                                 exist_ok=True)
        shutil.move(self.source_path, self.dest_path)

    def rollback(self):
        print("MoveAction rollback: move {} -> {}".format(
            self.dest_path, self.source_path))
        shutil.move(self.dest_path, self.source_path)
