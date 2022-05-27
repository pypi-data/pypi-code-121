"""gitea api操作
主要功能：
1.判断指定的branch/tag/commit是否存在；
2.创建tag;
3.创建release;
"""
# coding = utf-8
import os
import re
import json
import logging
import requests
from .git import parser_git_url
from .http import format_output


__all__ = ["is_checkout", "tetrieve_branch", "get_tags", "get_commit_default"]

logger = logging.getLogger("DengUtils")

DOMAIN = os.environ["GIT_CI_API_URL"]
ACCESS_TOKEN = os.environ["GIT_CI_TOKEN"]

# gitea api存在bug，apidoc中标明支持headers方式鉴权，但实际不支持
# auth_header = {"Authorization": ACCESS_TOKEN, "accept": "application/json; charset=UTF-8"}
auth_params = {"access_token": ACCESS_TOKEN}

session = requests.Session()
# session.headers.update(auth_header)


def checkout_response(response: requests.Response, level=""):
    """检查请求响应"""
    if response.status_code == 403 or response.status_code == 401:
        format_output(response, "error", depth=3)
        raise ValueError("权限认证失败，请检查！")

    if response.status_code >= 400:
        format_output(response, "error", depth=3)
    else:
        if level:
            format_output(response, level=level, depth=3)
        return response.json()


def is_checkout(*, owner: str, repo: str, target: str):
    """提供的branch/tag/commitId是否存在"""
    # gitea中允许branch与tag重名，必须区分优先级
    # tag优先级最高
    _res_tag = get_tags(owner=owner, repo=repo)
    if _res_tag:
        for _tag in _res_tag:
            if _tag["name"] == target:
                return _tag

    # branch优先级第二
    _res_branch = tetrieve_branch(owner=owner, repo=repo, branch=target)
    if _res_branch:
        return _res_branch

    # commit 优先级最低
    _res_commit = get_commit_default(owner=owner, repo=repo, sha=target)
    if _res_commit:
        return _res_commit

    logger.warning(f"在{owner}/{repo}的tag/branch/commit中找不到目标：{target}")
    return None


def is_checkout_by_obj(repos: dict, target: str):
    """提供的branch/tag/commitId是否存在"""
    # target预处理，target中可能带有前缀
    if ":" in target:
        _type, target = target.split(":", 1)
    else:
        _type = None

    # gitea中允许branch与tag重名，必须区分优先级
    # tag优先级最高
    owner, repo = parser_git_url(repos["repo_url"])
    _res_tag = get_tags(owner=owner, repo=repo)
    if _res_tag:
        for _tag in _res_tag:
            if _tag["name"] == target:
                repos["branch"] = f"TAG:{target}"
                return True, owner, repo, target, repos

    # branch优先级第二
    _res_branch = tetrieve_branch(owner=owner, repo=repo, branch=target)
    if _res_branch:
        repos["branch"] = f"BRANCH:{target}"
        return True, owner, repo, target, repos

    # commit 优先级最低
    _res_commit = get_commit_default(owner=owner, repo=repo, sha=target)
    if _res_commit:
        repos["branch"] = f"COMMIT:{target}"
        return True, owner, repo, target, repos

    logger.error(f"在{owner}/{repo}的tag/branch/commit中找不到目标：{target}")
    repos["branch"] = None
    return False, owner, repo, target, repos


def get_protection_branch(*, owner: str, repo: str, branch: str):
    """获取受保护分支"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/branch_protections/{branch}"
    _res = session.get(_url, params=auth_params)
    return checkout_response(_res)


def protection_branch(*, owner: str, repo: str, branch: str):
    """保护分支"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/branch_protections"
    payload = {
        "branch_name": branch,
        "enable_push": False,
        "enable_push_whitelist": False,
        "push_whitelist_usernames": [],
        "push_whitelist_teams": [],
        "push_whitelist_deploy_keys": False,
        "enable_merge_whitelist": True,
        "merge_whitelist_usernames": [],
        "merge_whitelist_teams": ["codereview-group"],
        "enable_status_check": False,
        "status_check_contexts": None,
        "required_approvals": 1,
        "enable_approvals_whitelist": True,
        "approvals_whitelist_username": [],
        "approvals_whitelist_teams": ["codereview-group"],
        "block_on_rejected_reviews": False,
        "block_on_outdated_branch": False,
        "dismiss_stale_approvals": False,
        "require_signed_commits": False,
        "protected_file_patterns": "",
    }
    _res = session.post(_url, params=auth_params, json=payload)
    return checkout_response(_res, level="info")


def cancel_protection_branch(*, owner: str, repo: str, branch: str):
    """取消分支保护"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/branch_protections/{branch}"
    _res = session.delete(_url, params=auth_params)
    if _res.status_code == 204:
        return True


def delete_branch(*, owner: str, repo: str, branch: str):
    """删除分支"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/branches/{branch}"
    assert branch not in ("master", "release")
    _res = session.delete(_url, params=auth_params)
    if _res.status_code == 204:
        return True


def tetrieve_branch(*, owner: str, repo: str, branch: str):
    """检索特定分支"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/branches/{branch}"
    _res = session.get(_url, params=auth_params)
    return checkout_response(_res, level="debug")


def create_branch(*, owner: str, repo: str, old_branch_name: str, new_branch_name: str):
    """创建新分支"""
    # 检查新分支是否存在，存在是直接返回
    new_branch = tetrieve_branch(owner=owner, repo=repo, branch=new_branch_name)
    if new_branch:
        return True, new_branch

    # 不存在时创建分支
    _url = f"{DOMAIN}/repos/{owner}/{repo}/branches"
    assert new_branch_name not in ("master", "release")
    payload = {"old_branch_name": old_branch_name, "new_branch_name": new_branch_name}
    _res = session.post(_url, params=auth_params, json=payload)
    if _res.status_code == 404:
        raise ValueError(f"{owner}/{repo}库找不到源分支：{old_branch_name}")
    data = _res.json()
    data["owner"] = owner
    data["repo"] = repo
    if _res.status_code == 201:
        return True, data
    else:
        return False, data


def get_tags(*, owner: str, repo: str):
    """获取库中tag标签列表"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/tags"
    _res = session.get(_url, params=auth_params)
    return checkout_response(_res)


def get_commit_default(*, owner: str, repo: str, sha: str):
    """获取commit详情"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/git/commits/{sha}"
    _res = session.get(_url, params=auth_params)
    return checkout_response(_res, level="debug")


def release_exists(
    *, owner: str, repo: str, name: str, tag_name: str, target: str
) -> dict:
    """判断release是否已经存在"""
    _release_list = get_releases(owner=owner, repo=repo)
    for _release in _release_list:
        if (
            _release["name"] == name
            and _release["tag_name"] == tag_name
            and _release["target_commitish"] == target
        ):
            logger.info(f"release已经存在：{owner}/{repo}:{name}")
            return _release
    logger.info(f"release不存在：{owner}/{repo}:{name}")
    return {}


def get_releases(*, owner: str, repo: str, page=1, per_page=100):
    """获取release列表"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/releases"
    params = {**auth_params, "page": page, "per_page": per_page}
    _res = session.get(_url, params=params)
    return checkout_response(_res)


def get_release_by_id(*, owner: str, repo: str, release_id: int):
    """获取release详情"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/releases/{release_id}"
    _res = session.get(_url, params=auth_params)
    return checkout_response(_res, level="debug")


def create_release(*, owner: str, repo: str, payload: dict) -> dict:
    """创建release"""
    # 先判断相应的release是否已经存在
    _release = release_exists(
        owner=owner,
        repo=repo,
        name=payload["name"],
        tag_name=payload["tag_name"],
        target=payload["target_commitish"],
    )
    if _release:
        return _release

    # 不存在时创建
    _url = f"{DOMAIN}/repos/{owner}/{repo}/releases"
    logger.info(
        f"【{owner}/{repo}】库发布版本，参数：{json.dumps(payload, ensure_ascii=False, indent=4)}"
    )
    _res = session.post(_url, params=auth_params, json=payload)
    return checkout_response(_res, level="info")


def batch_delete_release(release_list: list):
    """批量删除release"""
    for _release in release_list:
        _res = session.delete(_release["url"], params=auth_params)
        if _res.status_code == 204:
            logger.info(f"删除成功：{_release['url']}")
        elif _res.status_code == 404:
            logger.warning(f"记录不存在：{_release['url']}")
        else:
            format_output(_res)
            logger.error(f"删除失败：{_release['url']}")


def delete_release(*, owner: str, repo: str, release_id: int):
    """删除release"""
    release_obj = get_release_by_id(owner=owner, repo=repo, release_id=release_id)
    assert release_obj["id"] == release_id
    assert release_obj["prerelease"] is True, "非预发布状态，不能删除"
    assert release_obj["name"].startswith("temp_"), "release名字校验不通过，只有以temp_开头的才能删除"
    logger.info(f"可删除性校验通过，开始删除release: {release_obj['name']}")
    _url = f"{DOMAIN}/repos/{owner}/{repo}/releases/{release_id}"
    _res = session.delete(_url, params=auth_params)
    return checkout_response(_res, level="info")


def get_pulls(
    *, owner: str, repo: str, state: str, sort: str = "recentupdate", page=1, limit=50
):
    """获取pull列表"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/pulls"
    if isinstance(page, int):
        params = {"state": state, "sort": sort, "page": page, "limit": limit}
    else:
        params = {"state": state, "sort": sort, "page": 1, "limit": limit}
    params.update(auth_params)
    pull_list = []
    while True:
        _res = session.get(_url, params=params)
        _temp_pulls = checkout_response(_res)
        pull_list.extend(_temp_pulls)
        if len(_temp_pulls) < limit or isinstance(page, int):
            break
        else:
            params["page"] += 1
    return pull_list


def merge_audit(
    *,
    owner: str,
    repo: str,
    index: int,
    audit: str = "merge",
    title: str = "自动合并",
    body: str = "来自web-hock的自动合并",
):
    """审核Merge Request"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/pulls/{index}/merge"
    payload = {
        "Do": audit,
        "MergeMessageField": body,
        "MergeTitleField": title,
        "force_merge": False,
    }
    _res = session.post(_url, params=auth_params, json=payload)
    return _res.status_code


def get_pull_by_issue_id(*, owner: str, repo: str, issue_id: int):
    """获取指定issue详情"""
    _url = f"{DOMAIN}/repos/{owner}/{repo}/pulls/{issue_id}"
    _res = session.get(_url, params=auth_params)
    return checkout_response(_res, level="debug")


def merge_new(
    *,
    owner: str,
    repo: str,
    target: str,
    source: str,
    title: str = "hock自动发起",
    body: str = "hock监控到有往release分支的merge request时，自动往master上合并",
    exist_ok: bool = True,
):
    """发起merge request"""
    payload = {
        "base": target,
        "head": source,
        "body": body,
        "title": title,
    }
    _url = f"{DOMAIN}/repos/{owner}/{repo}/pulls"
    _res = session.post(_url, params=auth_params, json=payload)
    if (
        exist_ok
        and _res.status_code == 409
        and "pull request already exists for these targets" in _res.text
    ):
        logger.info("相应Merge Request 已经存在，无需再次创建，直接获取已经存在的内容")
        format_output(_res, "debug")
        _e = r"issue_id: (\d+?),"
        _r = re.search(_e, _res.text, re.I)
        issue_id = int(_r.groups()[0])
        return get_pull_by_issue_id(owner=owner, repo=repo, issue_id=issue_id)
    return checkout_response(_res, level="debug")


if __name__ == "__main__":
    pass
