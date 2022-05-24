from pathlib import (
    Path,
)
from typing import (
    Dict,
)

import git
from git import (
    InvalidGitRepositoryError,
    Repo,
)


def ls_remote(
    url: str,
) -> Dict[str, str]:
    """
    Аналог команды ls-remote для проверки удаленного репозитория
    """
    remote_refs = {}

    g = git.cmd.Git()

    for ref in g.ls_remote(url).split('\n'):
        hash_ref_list = ref.split('\t')
        remote_refs[hash_ref_list[1]] = hash_ref_list[0]

    return remote_refs


def clone_or_pull_repository(
    path: Path,
    url: str,
    branch: str = 'master',
):
    """
    Обновление репозитория с конфигурационными файлами тестовых стендов.

    Если директория не существует, то необходимо склонировать репозиторий.
    """
    repository = None

    if (
        path.exists() and
        path.is_dir()
    ):
        try:
            repository = Repo(
                path=str(path),
            )
        except InvalidGitRepositoryError:
            repository = None

    if not repository:
        repository = Repo.clone_from(
            url=url,
            to_path=str(path),
            branch=branch,
        )

    origin = repository.remotes.origin
    origin.pull()
