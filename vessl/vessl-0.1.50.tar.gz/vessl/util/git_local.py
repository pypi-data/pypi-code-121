import os
from typing import Optional, Tuple

from openapi_client.models import ResponseProjectInfo
from vessl import vessl_api
from vessl.util.exception import GitError
from vessl.util.git_local_repo import GitRepository
from vessl.util.uploader import Uploader


def get_git_repo() -> Tuple[Optional[str], Optional[str]]:
    if vessl_api.default_git_repo is None:
        raise GitError("Not in a git repository")

    owner, repo, _ = vessl_api.default_git_repo._get_github_repo()
    return owner, repo


def get_git_branch(**kwargs) -> Optional[str]:
    if vessl_api.default_git_repo is None:
        raise GitError("Not in a git repository")

    if "git_branch" in kwargs:
        return kwargs["git_branch"]
    if vessl_api.default_git_repo is not None:
        return vessl_api.default_git_repo.branch
    raise None


def get_git_ref(**kwargs) -> Optional[str]:
    if vessl_api.default_git_repo is None:
        raise GitError("Not in a git repository")

    git_ref = vessl_api.default_git_repo.commit_ref
    if "git_ref" in kwargs:
        git_ref = kwargs["git_ref"]

    if not vessl_api.default_git_repo.check_revision_in_remote(git_ref):
        raise GitError(f"Git commit does not exist in a remote repository: {git_ref}")

    return git_ref


def get_git_diff_path(project: ResponseProjectInfo, **kwargs) -> Optional[str]:
    if vessl_api.default_git_repo is None:
        raise GitError("Not in a git repository")

    use_git_diff = kwargs.get("use_git_diff", True)
    use_git_diff_untracked = kwargs.get("use_git_diff_untracked", True)

    if not use_git_diff:
        return None

    has_diff, _ = GitRepository.get_current_diff_status(
        revision_or_branch=get_git_ref()
    )
    if not has_diff:
        return None

    local_file = GitRepository.get_current_diff_file(
        revision_or_branch=get_git_ref(), with_untracked=use_git_diff_untracked
    )

    remote_file = Uploader.upload(
        local_path=local_file.name,
        volume_id=project.volume_id,
        remote_path=os.path.basename(local_file.name),
    )

    local_file.close()
    return remote_file.path
