#!/usr/bin/python3
# coding = utf-8
# @Time: 2020/8/18 12:05
# @Author: DengQingYong
# @Email: it_dqy@qq.com
import os
import re
import time
import logging
from typing import Union
from pathlib import Path
from . import utils, message, file


logger = logging.getLogger("DengUtils")


def check_branch_exist(
    repo_path: Union[str, Path], branch: str, remote: str = ""
) -> bool:
    """检查指定分支是否存在"""
    repo_path = Path(repo_path)

    file.check_path_is_exits(repo_path, path_type="dir")
    os.chdir(repo_path)

    if remote:
        try:
            utils.execute_cmd(
                ["git", "fetch", remote, branch], level="debug", ignore_error_log=True
            )
        except Exception as e:
            logger.debug(f"【{repo_path}】远程库中不存在【{branch}】分支")
            return False
        else:
            logger.debug(f"【{repo_path}】远程库中存在【{branch}】分支")
            return True
    else:
        try:
            utils.execute_cmd(
                ["git", "checkout", branch], level="debug", ignore_error_log=True
            )
        except Exception as e:
            logger.debug(f"【{repo_path}】本地库中不存在【{branch}】分支")
            return False
        else:
            logger.debug(f"【{repo_path}】本地库中存在【{branch}】分支")
            return True


def get_current_branch(repo_path: Union[str, Path]) -> tuple:
    """获取当前分支"""
    repo_path = Path(repo_path)
    file.check_path_is_exits(repo_path, path_type="dir")
    os.chdir(repo_path)
    try:
        _res = utils.execute_cmd(["git", "status"], level="debug")
    except Exception as e:
        return "", ""
    else:
        b_pattern_en = r"^On branch (.+)$"
        b_pattern_cn = r"^位于分支 (.+)$"
        t_pattern_en = r"^HEAD detached at (.+)$"
        t_pattern_cn = r"^头指针分离于 (.+)$"
        for _line in _res.stdout.split("\n"):
            for pattern in (b_pattern_en, b_pattern_cn, t_pattern_en, t_pattern_cn):
                _res = re.search(pattern, _line, re.I)
                if _res:
                    _value = _res.groups()[0]
                    if "branch" in pattern or "分支" in pattern:
                        return "BRANCH", _value
                    else:
                        if len(_value) == 7:
                            return "COMMIT", _value
                        else:
                            return "TAG", _value
        raise ValueError(f"获取{repo_path}git库当前分支信息失败")


def push_local_update(
    repo_path: Path, branch: str, commit_desc: str, receiver: str = ""
) -> str:
    """push本地修改到远程分支"""
    logger.info(push_local_update.__doc__ + commit_desc)
    file.check_path_is_exits(repo_path, path_type="dir")
    os.chdir(str(repo_path))
    exist_update = False
    try:
        _res = utils.execute_cmd(["git", "status"])
        if (
            "Untracked files:" in _res.stdout
            or "Changes not staged for commit:" in _res.stdout
            or "尚未暂存以备提交的变更：" in _res.stdout
            or "未跟踪的文件:" in _res.stdout
        ):
            exist_update = True
            utils.execute_cmd(["git", "add", "."])
            current_time = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
            utils.execute_cmd(["git", "commit", "-m", current_time + commit_desc])

        if (
            exist_update
            or "Your branch is ahead of" in _res.stdout
            or "您的分支领先" in _res.stdout
        ):
            utils.execute_cmd(["git", "push", "origin", branch])
    except Exception as e:
        _msg = f"{repo_path}仓库push失败存在冲突，请手动处理！"
        logger.error(_msg)
        logger.exception(e)
        if receiver:
            message.send_text_alert_message(_msg + "\n" + str(e), receiver)
        return "fail"
    else:
        if exist_update:
            logger.debug(f"push成功：{repo_path}")
            return "success"
        else:
            logger.info(f"本地没有更新，忽略：{repo_path}")
            return "noupdate"


def init_repo(
    repo_path: Union[str, Path], repo_url: str, lfs: bool = False, pattern=None
) -> bool:
    """初始化本地库"""
    repo_path = Path(repo_path)

    def __enable_sparse_checkout(_repo_path: Path, _pattern: str):
        """开启稀疏签出"""
        os.chdir(_repo_path)
        logger.debug(f"更新【稀疏签出】，签出表达式：{_pattern}")
        utils.execute_cmd(
            ["git", "config", "core.sparsecheckout", "true"], level="debug"
        )
        _checkout_config = _repo_path / ".git" / "info" / "sparse-checkout"
        with open(str(_checkout_config), "w") as _f:
            _f.write(_pattern)

    logger.debug(init_repo.__doc__ + f"{repo_path}：开始")
    if not repo_path.exists():
        repo_path.mkdir(exist_ok=True, parents=True)
    if repo_path.is_file():
        file.ensure_empty_dir(repo_path)

    os.chdir(repo_path)
    # 非git库时初始化为git库
    _git = repo_path / ".git"
    if _git.exists():
        is_new_repo = False
        logger.debug(init_repo.__doc__ + f"{repo_path}：已经是git库，忽略")
        # 更新稀疏签出配置
        if pattern:
            __enable_sparse_checkout(repo_path, pattern)
    else:
        is_new_repo = True
        utils.execute_cmd(["git", "init"])
        utils.execute_cmd(["git", "remote", "add", "origin", repo_url])
        if pattern:
            __enable_sparse_checkout(repo_path, pattern)
        if lfs:
            utils.execute_cmd(["git", "lfs", "install"])
        logger.info(init_repo.__doc__ + f"{repo_path}：完成")
    return is_new_repo


def pull_repo(
    repo_path: Union[str, Path],
    repo_url: str,
    branch: str,
    branch_type: str = "branch",
    remote: str = "origin",
    lfs: bool = False,
    pattern: str = None,
    no_exist_create_modle: str = None,
    consistency_check: bool = True,
):
    """拉取代码"""
    start_time = time.perf_counter()
    repo_path = Path(repo_path)
    _, repo_name = parser_git_url(repo_url)
    is_new_repo = init_repo(repo_path, repo_url, lfs, pattern)

    # 丢弃本地所有修改
    if not is_new_repo:
        res = utils.execute_cmd(["git", "status"], level="debug")
        # 工作目录干净，不需要处理
        if (
            "nothing to commit, working tree clean" in res.stdout
            or "无文件要提交，干净的工作区" in res.stdout
        ):
            pass
        # 工作目录不干净，丢弃本地所有修改
        else:
            # 撤消暂存区所有的变更
            # utils.execute_cmd(["git", "reset", "--hard", "HEAD"], level="debug")
            # 清空工作区所有的变更
            utils.execute_cmd(["git", "checkout", "."], level="debug")
            # 丢弃本地新增与删除的
            utils.execute_cmd(["git", "clean", "-df"], level="debug")

    # 检查远程是否存在指定分支
    if branch_type == "branch":
        branch_exist = check_branch_exist(repo_path, branch, remote=remote)
        if branch_exist:
            # 远程分支存在时拉取更新
            utils.execute_cmd(["git", "fetch", remote, branch], level="debug")
            utils.execute_cmd(["git", "checkout", branch], level="debug")
            utils.execute_cmd(["git", "merge"], level="debug")
        else:
            # 远程分支不存在时判断本地是否存在指定分支
            branch_exist = check_branch_exist(repo_path, branch)
            if branch_exist:
                # 本地存在指定分支时直接推送到远程，并建立跟踪
                utils.execute_cmd(["git", "push", "-u", remote, branch])
            else:
                if no_exist_create_modle and no_exist_create_modle != branch:
                    # 本地不存在时基于模板分支创建指定分支
                    utils.execute_cmd(["git", "branch", branch, no_exist_create_modle])
                    utils.execute_cmd(["git", "checkout", branch])
                    utils.execute_cmd(["git", "push", "-u", remote, branch])
                else:
                    raise ValueError(f"库{repo_name}远程分支不存在：{branch}")

        # 检查本地分支与远程分支是否一致
        res = utils.execute_cmd(["git", "status"], level="debug")
        # 工作目录干净，不需要处理
        if (
                f"Your branch is up to date with '{remote}/{branch}'." in res.stdout
                or f"您的分支与上游分支 '{remote}/{branch}' 一致。" in res.stdout
        ):
            logger.debug(f"仓库{repo_path}分支{branch}与上游{remote}/{branch}分支一致")
        else:
            output_str = utils.bytes_to_str(res.stdout)
            logger.warning(output_str)
            if consistency_check:
                raise ValueError("分支不一致\n" + output_str)
            else:
                logger.warning(f"仓库{repo_path}分支{branch}与上游{remote}/{branch}分支不一致")
    elif branch_type == "tag":
        try:
            # 拉取指定tag或是本地不存在但远程存在的tag
            # 已有的tag不会对比，防止本地已有tag与远程相应tag不一致时出现冲突报错
            utils.execute_cmd(["git", "fetch", remote, "tag", branch], level="debug")
        except Exception as _err:
            logger.exception(_err)
            logger.error(f"拉取tag {branch}出错，删除本地{branch}后重试")
            # 出错后——通常是本地与远程tag不一致有冲突导致的
            # 冲突后删除本地重新从远程拉取
            utils.execute_cmd(["git", "tag", "-d", branch], level="debug")
            utils.execute_cmd(["git", "fetch", remote, "tag", branch], level="debug")
        utils.execute_cmd(["git", "checkout", branch], level="debug")
    elif branch_type == "commit":
        # 先检查本地是否已经为预计目标，如果是则不用访问远程git服务，防止远程git服务不可用导致额外的报错
        # 只适用于commit类型，因为只有commit是不可变的，branch是可变的，tag可以删除后重新创建同名标签
        current_type, current_branch = get_current_branch(repo_path)
        if (
            branch_type == "commit"
            and branch_type == current_type.lower()
            and branch == current_branch
        ):
            logger.info(f"当前已经是预定目标，无需切换：{branch_type}:{branch}:{repo_path}")
        else:
            utils.execute_cmd(["git", "fetch", remote, "master"], level="debug")
            utils.execute_cmd(["git", "checkout", branch], level="debug")
    else:
        raise ValueError(f"库{repo_name}目标类型错误，必须为branch,tag,commit中的一种")

    if lfs:
        utils.execute_cmd(["git", "lfs", "pull"], level="debug")
    elapsed = round(time.perf_counter() - start_time, 3)
    logger.info(pull_repo.__doc__ + f"，仓库：{repo_path}，分支：{branch}，耗时：{elapsed}秒")


def merge_to_branch(
    repo_path: Union[str, Path], repo_url: str, target_branch: str, source_branch: str
) -> str:
    """将源分支代码合并进目标分支
    :param repo_path: 仓库绝对路径
    :param repo_url: 操作库ssh地址
    :param target_branch: 目标分支，当前操作分支，将源合并进此分支
    :param source_branch: 源分支
    """
    repo_path = Path(repo_path)

    logger.info(f"开始合并分支，仓库路径：{repo_path}，目标分支：{target_branch}，源分支：{source_branch}")
    # 更新源分支
    pull_repo(repo_path, repo_url, source_branch)
    # 更新目标分支
    pull_repo(repo_path, repo_url, target_branch)

    # 冲突标识文件，出现冲突时创建此文件，冲突解决后删除此文件
    conflict = Path(repo_path) / "merge-conflict.txt"

    try:
        # 将源分支代码到目标分支上
        utils.execute_cmd(["git", "merge", source_branch])
    except Exception as e:
        logger.error(f"合并失败：{str(e)}")
        if "Merge conflict" in str(e):
            merge_result = "merge conflict"
            conflict.touch(exist_ok=True)
        else:
            merge_result = f"unknown error：{str(e)}"
        logger.info("中止merge操作")
        try:
            utils.execute_cmd(["git", "merge", "--abort"])
        except Exception as _e:
            logger.warning(_e)
    else:
        # 推送代码
        utils.execute_cmd(["git", "push", "origin", target_branch])
        logger.info(
            f"分支合并到完成，仓库路径：{repo_path}，目标分支：{target_branch}，源分支：{source_branch}"
        )

        # merge成功后检查冲突标志文件是否存在，存在则删除
        if conflict.exists():
            conflict.unlink()
            merge_result = "resolve conflict pass"
        else:
            merge_result = "one pass"

    return merge_result  # 合并结果：一次性通过、冲突、解决冲突后通过


def parser_git_url(repo_url: str) -> tuple:
    """从git库地址中获取owner信息"""
    repo_url = repo_url.replace(".git", "")
    if repo_url.startswith("http"):
        return repo_url.split("/")[-2], repo_url.split("/")[-1]
    elif repo_url.startswith("git"):
        return repo_url.split("/")[-2].split(":")[-1], repo_url.split("/")[-1]
    else:
        return None, None


def get_repo_info(repo_path: Union[str, Path], remote="origin"):
    """获取指定git库信息"""
    repo_path = Path(repo_path)

    _type, _value = get_current_branch(repo_path)
    try:
        _res = utils.execute_cmd(["git", "remote", "get-url", "--push", remote])
    except utils.ExecuteCMDException as e:
        logger.warning(f"目标目录是git仓库，但没有关联远程库：{repo_path}")
        return {}
    else:
        _owner, _repo = parser_git_url(_res.stdout.strip())
        return {
            "owner": _owner,
            "repo": _repo,
            "url": _res.stdout.strip(),
            "path": repo_path,
            "current_branch": f"{_type}:{_value}",
        }


def create_branch_by_tag(
    repo_path: Union[str, Path], tag_name: str, branch_name: str, push: bool = True
) -> bool:
    """根据tag/branch/commit创建新分支
    :param repo_path: git库本地绝对路径
    :param tag_name: 基于此对象创建新分支，可以是tag或branch或commit
    :param branch_name: 新分支名称
    :param push: 创建分支后是否推送到远程origin
    """
    repo_path = Path(repo_path)

    file.check_path_is_exits(repo_path, path_type="dir")
    os.chdir(repo_path)

    # 清空工作区所有的变更
    utils.execute_cmd(["git", "checkout", "."], level="debug")
    # 丢弃本地新增与删除的
    utils.execute_cmd(["git", "clean", "-dfx"], level="debug")

    # 检查远程库中是否已经存在相应分支
    remote_has_branch = check_branch_exist(repo_path, branch_name, remote="origin")
    if remote_has_branch:
        logger.warning(f"远程库中已经存在{branch_name}分支")
        return True

    # 检查本地库中是否已经存在相应分支
    local_has_branch = check_branch_exist(repo_path, branch_name)
    if local_has_branch:
        logger.warning(f"本地库中已经存在{branch_name}分支")
    else:
        # 开始创建新分支
        utils.execute_cmd(["git", "branch", branch_name, tag_name])
    # 切换到新分支
    utils.execute_cmd(["git", "checkout", branch_name])
    if push:
        # 将新分支推送到远程库
        utils.execute_cmd(["git", "push", "-u", "origin", branch_name])
    return True
