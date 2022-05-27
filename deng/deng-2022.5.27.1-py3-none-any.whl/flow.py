import os
import re
import json
import time
from pathlib import Path
from typing import Union, List

from . import logger, file as file_utils


def get_engine_version_info(deputy_abs_path: Union[str, Path]) -> dict:
    """获取引擎版本信息"""
    file_utils.check_path_is_exits(deputy_abs_path, path_type="file")
    version_path = Path(deputy_abs_path).parent / "version.txt"
    file_utils.check_path_is_exits(version_path, path_type="file")
    version_info = dict()
    with open(version_path, encoding="utf-8") as _file:
        try:
            _file_version_info = json.load(_file)
        except Exception as e:
            raise ValueError(f"版本文件解析出错：{version_path}")

    version_info["arch"] = _file_version_info["InstructionSet"]
    # 兼容三段版本号与四段版本号
    version_info["raw_version"] = _file_version_info["Version"]
    _temp_version_list = version_info["raw_version"].split(".")
    if len(_temp_version_list) == 4:
        version_info["version"] = ".".join(_temp_version_list[:-1])
    elif len(_temp_version_list) == 3:
        version_info["version"] = _file_version_info["Version"]
    else:
        raise ValueError(f"引擎版本出现未知情况：{_file_version_info}")
    version_info["language"] = _file_version_info.get("Language", "zh-cn")
    version_info["build_date"] = _file_version_info["Build"]

    product_name_list = _file_version_info["Product"].lower().split()
    version_info["edition"] = product_name_list[-1]
    if len(product_name_list) == 3:
        version_info["package"] = product_name_list[1]
    else:
        version_info["package"] = "creator"

    return version_info


def get_flow_info(flow_path: Union[Path, str]):
    """从流程flow文件中读取流程信息"""
    if isinstance(flow_path, str):
        flow_path = Path(flow_path)
    if flow_path.is_dir():
        flow_file_abs_path = flow_path / "main.prj"
        if not flow_file_abs_path.exists():
            flow_file_abs_path = flow_path / f"{flow_path.name}.flow"
    else:
        flow_file_abs_path = flow_path
    file_utils.check_path_is_exits(flow_file_abs_path, path_type="file")
    with open(flow_file_abs_path, encoding="utf-8") as _file:
        flow_config = json.load(_file)
    return flow_config


def update_flow_info(flow_path: str, flow_info: dict):
    """更新流程flow文件信息"""
    file_utils.check_path_is_exits(flow_path)
    flow_path = Path(flow_path)
    if flow_path.is_dir():
        flow_file_path = flow_path / f"{flow_path.name}.flow"
    else:
        flow_file_path = flow_path
    file_utils.check_path_is_exits(flow_file_path, path_type="file")
    # 备份flow文件
    file_utils.copy_to_target(flow_file_path, str(flow_file_path) + str(time.time()) + ".bak")
    with open(flow_file_path, mode="w", encoding="utf-8") as _file:
        json.dump(flow_info, _file, ensure_ascii=False, indent=4)


def compare_version_number(version_a: str, version_b: str, level: int = 3) -> int:
    """获取最后的版本信息
    :param version_a: str, 比较参数1
    :param version_b: str, 比较参数2
    :param level: int, 比较等级，0时全版本比较，1时仅比较第一个大版本，2时比较前2个版本号，3号比较前3个版本号
    """
    a = version_a.split(".")
    b = version_b.split(".")
    if len(a) != len(b):
        raise ValueError(f"版本格式不一致，无法比较：{version_a}，{version_b}")
    for i in range(len(a[:level])):
        res = int(a[i]) - int(b[i])
        if res != 0:
            return res
    return 0


def flow_global_param_convert(flow_params: list, target_type) -> list:
    """流程全局参数转换"""
    new_flow_params = []
    _msg_old = "将flow转换成5.2.0以前版本格式"
    _msg_new = "将flow转换成5.2.0及以后版本格式"
    for param in flow_params:
        if isinstance(param, target_type):
            new_flow_params.append(param)
            continue

        if target_type == str:
            if _msg_old:
                logger.info(_msg_old)
                _msg_old = None
            if param["type"] == "none":
                new_flow_params.append(param["var"])
            else:
                raise ValueError(f"流程中用到了子流程，无法转换成5.2.0以前的版本，不兼容！")
        elif target_type == dict:
            if _msg_new:
                logger.info(_msg_new)
                _msg_new = None
            temp = {"var": param, "type": "none"}
            new_flow_params.append(temp)
    return new_flow_params


def get_next_version(version: str) -> str:
    """获取下一版本号"""
    v = version.split(".")
    last_number = str(int(v.pop()) + 1)
    v.append(last_number)
    return ".".join(v)


def is_ignore(ignore_path: Path, flow_file_path: Path) -> bool:
    """判断是否忽略流程"""
    try:
        file_utils.check_path_is_exits(ignore_path, path_type="file")
    except FileNotFoundError as _e:
        logger.warning(f"忽略列表文件不存在，不忽略任何流程")
        return False

    with open(ignore_path, encoding="utf-8") as _file:
        for _line in _file:
            _line = _line.strip()
            # 跳过空行
            if not _line:
                continue
            # 跳过注释行
            if _line.startswith("//"):
                continue
            # 解析配置行
            if "=" in _line:
                try:
                    _type, _value = _line.split("=", 1)
                    # 去掉=两边的空格
                    _type = _type.strip()
                    _value = _value.strip()
                except Exception as _e:
                    # 跳过无效配置行
                    continue
                else:
                    # 按路径忽略
                    if _type.lower() == "path":
                        _item_ignore_path = ignore_path.parent / _value
                        if _item_ignore_path.exists():
                            # 具体到流程文件
                            if _item_ignore_path == flow_file_path:
                                return True
                            # 按目录忽略
                            if _item_ignore_path in flow_file_path.parents:
                                return True
                    # 按流程名称忽略
                    elif _type.lower() == "name":
                        if flow_file_path.stem == _value:
                            return True
                    else:
                        # 跳过无效配置行
                        continue
            else:
                # 跳过无效配置行
                continue
    # 前面逻辑都未匹配时
    return False


def is_author(author, flow_file_path: Path) -> bool:
    """判断author是否为流程作者"""
    return get_flow_author(flow_file_path) == author


def get_file_list_by_suffix(
    target: Path,
    suffix: str,
    reverse: bool = True,
    depth=2,
    flow_version: str = None,
    flow_name: str = None,
    ignore_path: Path = None,
    only_author: str = None,
    ignore_author: str = None,
) -> List[Path]:
    """获取目标文件夹下的特定扩展文件列表"""
    file_list = []
    # 兼容带.与不带.
    suffix = suffix.strip().strip(".")
    for flow_path in target.glob(f"**/*.{suffix}"):
        # 递归尝试过滤
        if len(flow_path.parts) - len(target.parts) > depth:
            logger.info(f"超过递归深度【{depth}】，忽略：{flow_path}")
            continue

        # 仅运行指定流程
        _flow_name = get_flow_name(flow_path)
        if flow_name and _flow_name != flow_name:
            logger.info(f"不满足指定流程名称【{flow_name}】，忽略：{flow_path}")
            continue

        # 仅运行指定版本的流程
        if flow_version and get_flow_version(flow_path) != flow_version:
            logger.info(f"版本不满足指定要求【{flow_version}】，忽略：{flow_path}")
            continue

        # 按流程忽略列表过滤——判断是否为忽略流程
        if ignore_path and is_ignore(ignore_path, flow_path):
            logger.info(f"匹配忽略配置文件，忽略：{flow_path}")
            continue

        # 仅运行指定作者的流程
        if only_author and get_flow_author(flow_path) != only_author:
            logger.info(f"不满足仅运行指定作者{only_author}的流程，忽略：{flow_path}")
            continue

        # 忽略指定作者的流程
        if ignore_author and get_flow_author(flow_path) == ignore_author:
            logger.info(f"满足忽略指定作者{only_author}的流程，忽略：{flow_path}")
            continue

        # 忽略包含子流程的流程
        if "子流程" in str(flow_path):
            logger.info(f"不支持包含子流程的流程，忽略：{flow_path}")
            continue

        # 流程满足以上所有条件，加入待运行列表
        file_list.append(flow_path)

    file_list.sort(reverse=reverse)
    return file_list


def get_flow_version(flow_file_abs_path: Path):
    """获取流程版本"""
    file_utils.check_path_is_exits(flow_file_abs_path, path_type="file")
    flow_version_file_path = flow_file_abs_path.parent / "res" / "version.txt"
    with open(flow_version_file_path, encoding="utf-8") as _file:
        return _file.read().strip()


def get_flow_author(flow_file_abs_path: Path):
    """获取流程作者"""
    file_utils.check_path_is_exits(flow_file_abs_path, path_type="file")
    flow_author_file_path = flow_file_abs_path.parent / "res" / "author.txt"
    with open(flow_author_file_path, encoding="utf-8") as _file:
        return _file.read().strip()


def is_uuid(_uuid: str):
    """判断字符串是否为uuid格式"""
    if len(_uuid) != 36:
        return False

    _e = r"([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})"
    _res = re.match(_e, _uuid)
    if _res:
        return _res.groups()[0]
    else:
        return False


def is_version_no(version: str):
    """判断字符串是否为uuid格式"""
    _e = r"([1-9]{1}.[0-9]{1}.[0-9]{1})"
    _res = re.match(_e, version)
    if _res:
        return _res.groups()[0]
    else:
        return False


def get_flow_name(flow_file_abs_path: Union[str, Path]) -> str:
    """获取流程名称"""
    _flow_name = None
    file_utils.check_path_is_exits(flow_file_abs_path, path_type="file")
    flow_file_abs_path = Path(flow_file_abs_path)
    # 6.0.0版本以前的老流程
    # 所有版本的bot包
    if flow_file_abs_path.stem.lower() != "main":
        _flow_name = flow_file_abs_path.stem
    # 6.0.0及以后版本的流程
    elif flow_file_abs_path.suffix.lower() == ".prj":
        info_json = file_utils.read_file_content(
            flow_file_abs_path, encoding="utf-8", _return="json"
        )
        _flow_name = info_json["name"]
    else:
        # Worker 中运行时bot包缓存目录
        config_path = flow_file_abs_path.parent / "config.json"
        info_json = file_utils.read_file_content(
            config_path, encoding="utf-8", _return="json"
        )
        _flow_name = info_json["name"]
    return _flow_name


def clean_flow(flow_dir_path: Path):
    """清理流程目录中的临时文件"""
    # 清理数据：临时文件，后续生成.bot包时会重新生成这些文件
    file_utils.check_path_is_exits(flow_dir_path, path_type="dir")
    for item in flow_dir_path.iterdir():
        if item.is_file() and item.suffix in [".bot", ".flowc", ".taskc", ".cme", ".bak"]:
            item.unlink()
            continue

        if item.name.lower() in ["log", "tempgit", "config.json", ".git"]:
            if item.is_file():
                item.unlink()
            else:
                file_utils.rm(item)
