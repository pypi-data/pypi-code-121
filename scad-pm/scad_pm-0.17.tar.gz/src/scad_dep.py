import os.path
from dataclasses import dataclass


@dataclass
class Dep:
    path: str
    git_url: str
    repo_dir: str
    skip: bool

    def full_dir(self):
        return os.path.join(self.path, self.repo_dir)
