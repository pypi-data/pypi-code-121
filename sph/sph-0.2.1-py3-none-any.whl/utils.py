import typing
from pathlib import Path
from dataclasses import dataclass

import click
from git import Repo
from github import Repository


def delete_term_n_previous_line(n):
    for i in range(n):
        click.get_text_stream('stdout').write('\033[A\r\033[K')


Editable = typing.NewType('Editable', None)


@dataclass
class Editable:
    full_name: str
    name: str
    conan_path: Path
    required_lib: [Editable]
    repo: Repo
    gh_repo_client: Repository
    updated: bool = False
