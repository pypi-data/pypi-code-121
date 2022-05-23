from os import path
from typing import Callable, Optional
from git import Repo, PathLike
from shutil import rmtree

from dotpyle.utils.path import get_configuration_path, get_default_path
from dotpyle.services.logger import Logger


class RepoHandler:
    def __init__(
        self, logger: Logger, local_path: PathLike = get_default_path()
    ) -> None:
        self.logger = logger

        self.local_path = local_path
        if path.exists(local_path):
            self.repo = Repo(local_path)

    def __str__(self) -> str:
        return "RepoHandler tracking {}".format(self.local_path)

    def clone(
        self,
        remote_url: PathLike,
        force: bool = False,
        progress_listener: Optional[Callable] = None,
        branch_name: str = None,
    ) -> Repo:
        if path.exists(self.local_path):
            if force:
                self.logger.warning(
                    "Forcing operation. Make sure you know what you are doing!"
                )
                self.logger.warning("Removing config folder...")
                rmtree(self.local_path)
            else:
                raise FileExistsError(
                    "Default path already exists. Please use --force to"
                    " override."
                )

        self.repo = Repo.clone_from(
            url=remote_url,
            to_path=self.local_path,
            progress=progress_listener,
            branch=branch_name,
        )
        return self.repo

    def add(self, paths, config_file_changed=False):
        # self.repo.git.add(all=True)
        print("RepoHandler add: {}".format(paths))
        self.repo.git.add(paths)
        if config_file_changed:
            print("RepoHandler config file changed", get_configuration_path())
            self.repo.git.add(get_configuration_path())

    def commit(self, message):
        self.repo.index.commit(message)

    def push(self):
        self.repo.git.push()

    def pull(self):
        self.repo.git.pull()

    def check_changes(self, path):
        diff_index = self.repo.index.diff(None, path)
        print(self.repo.git.diff(path))
        len(list(diff_index.iter_change_type("M"))) > 0

        # for diff_item in diff_index.iter_change_type('M'):
        # print(diff_item)
        # print("A blob:\n{}".format(diff_item.a_blob.data_stream.read().decode('utf-8')))
        # print("B blob:\n{}".format(diff_item.b_blob.data_stream.read().decode('utf-8')))
        # return self.repo.git.status()
        # return self.repo.index.diff(self.repo.head.commit)
        # return self.repo.head.commit.diff()

        # for diff in self.repo.head.commit.diff('HEAD~1'):
