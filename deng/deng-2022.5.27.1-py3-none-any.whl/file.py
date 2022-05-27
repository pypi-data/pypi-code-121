import os
import re
import json
import time
import stat
import shutil
import tarfile
import zipfile
import logging
import datetime
import configparser
from pathlib import Path
from typing import Union


logger = logging.getLogger("DengUtils")


def check_path_is_exits(src_path: Union[str, Path], path_type=None):
    """检查目录或文件是否存在
    :param src_path: 源路径
    :param path_type: 源路径类型，可选值：file/dir
    """
    if isinstance(src_path, str):
        src_path = Path(src_path)

    if not src_path.exists():
        raise FileNotFoundError(f"目录或文件不存在：{src_path}")

    if path_type and path_type.lower() not in ("file", "dir"):
        raise ValueError("参数path_type非法，可选值有：file/dir")

    if path_type and path_type.lower() == "file":
        if not src_path.is_file():
            raise FileNotFoundError(f"{src_path}不是有效的文件！")

    if path_type and path_type.lower() == "dir":
        if not src_path.is_dir():
            raise FileNotFoundError(f"{src_path}不是有效的目录！")


def ensure_empty_dir(
    target: Union[str, Path], mkdir=True, parents=True, *args, **kwargs
) -> None:
    """确保目录为空目录
    :param target: 目标目录路径
    :param mkdir: bool, 目标目录不存在时自动创建
    :param parents: bool, 是否递归创建目录
    """
    if isinstance(target, str):
        target = Path(target)

    # 删除目录时，时常报拒绝访问的错误，增加重试次数
    for _ in range(10):
        try:
            if target.exists():
                if target.is_dir() and len(os.listdir(str(target))) == 0:
                    logger.info(f"已经是空目录：{target}")
                else:
                    if target.is_dir():
                        shutil.rmtree(target, ignore_errors=False)
                        logger.info(f"删除非空目录成功：{target}")
                    else:
                        target.unlink()
                        logger.info(f"删除文件成功：{target}")
                    # 防止报错，有时rmtree删除命令返回成功，但目录并还没有被删除完成，直接创建目录会报错
                    time.sleep(2)
                    if mkdir:
                        target.mkdir(parents=parents)
                        logger.info(f"创建目录成功：{target}")
            else:
                if mkdir:
                    target.mkdir(parents=parents)
                    logger.info(f"创建目录成功：{target}")
        except Exception as e:
            logger.exception(e)
            time.sleep(1)
        else:
            break
    else:
        raise ValueError(f"删除目录出错：{target}")


def compress_zip(src_path: str, compress_abs_path: str) -> None:
    """压缩zip文件
    :param src_path: 待压缩文件或目录路径
    :param compress_abs_path: 压缩包输出绝对路径
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)

    with zipfile.ZipFile(compress_abs_path, "w", zipfile.ZIP_DEFLATED) as compress_file:
        if os.path.isdir(src_path):
            for abs_dir_path, dir_list, file_list in os.walk(src_path):
                relative_path = abs_dir_path.replace(src_path, "")
                relative_path = (relative_path and relative_path + os.sep) or ""
                for filename in file_list:
                    compress_file.write(
                        os.path.join(abs_dir_path, filename), relative_path + filename
                    )
        else:
            filename = os.path.basename(src_path)
            compress_file.write(src_path, filename)


def extract_zip(src_zip: Union[str, Path], dst_dir: Union[str, Path]) -> None:
    """解压zip文件
    :param src_zip: str or Path, 需要解压的zip文件绝对路径
    :param dst_dir: str or Path, 解压后存储的目标目录
    """
    if isinstance(src_zip, str):
        src_zip = Path(src_zip)
    if isinstance(dst_dir, str):
        dst_dir = Path(dst_dir)

    # zip文件不存在时报错
    if not src_zip.exists():
        raise ValueError(f"zip文件不存在：{src_zip}")

    # 解压目录不存在时新建
    if not dst_dir.exists():
        dst_dir.mkdir(parents=True)

    if dst_dir.is_file():
        raise ValueError(f"{dst_dir}不是一个有效的目录")

    if zipfile.is_zipfile(src_zip):
        fz = zipfile.ZipFile(src_zip, "r")
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        raise ValueError(f"{src_zip}不是一个有效的zip文件")


def compress_tgz(source_files: str, compress_name: str):
    """将源文件打包成tar.gz格式
    :param source_files：str, 源文件路径，传入相对路径时，压缩包中也为相当路径，为绝对路径时，压缩包中同样为绝对路径
    :param compress_name: str, 生成的压缩包路径
    """
    # 判断文件是否存在，不存在时抛错
    if not os.path.exists(source_files):
        raise FileNotFoundError(source_files)

    with tarfile.open(compress_name, "w:gz") as tar:
        if os.path.isdir(source_files):
            for root, _dir, files in os.walk(source_files):
                for file in files:
                    fullpath = os.path.join(root, file)
                    tar.add(fullpath)
        else:
            tar.add(source_files)


def uncompress_tgz(compress_file, target_path="."):
    """解压tar.gz格式文件
    :param compress_file: str, 压缩包路径
    :param target_path: str, 解压后存储路径
    """
    tar = tarfile.open(compress_file)
    names = tar.getnames()
    for name in names:
        tar.extract(name, path=target_path)
    tar.close()


def rm(src_path: Union[str, Path], *args, **kwargs):
    """删除文件或目录
    :param src_path: str, 源文件或目录路径
    """
    check_path_is_exits(src_path)

    # 统一转换成Path处理
    if isinstance(src_path, str):
        src_path = Path(src_path)

    if src_path.is_file():
        src_path.unlink()
    else:
        shutil.rmtree(str(src_path), onerror=rm_readonly)

    logger.info(f"删除成功：{src_path}")


def rm_readonly(fn, tmp, info):
    """删除只读文件"""
    os.chmod(tmp, stat.S_IWRITE)
    if os.path.isfile(tmp):
        os.remove(tmp)
    elif os.path.isdir(tmp):
        shutil.rmtree(tmp)


def move_to_dir(
    src_path: Union[str, Path], dst_path: Union[str, Path], *args, **kwargs
):
    """移动文件
    :param src_path: str or Path, 源文件或目录路径
    :param dst_path: str or Path, 目标文件或目录路径
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path)

    check_path_is_exits(src_path)
    if not dst_path.exists():
        dst_path.mkdir(parents=True)
    shutil.move(str(src_path), str(dst_path))


def copy_to_target(
    src_path: Union[str, Path], dst_path: Union[str, Path], *args, **kwargs
):
    """复制文件或目标到目标路径
    :param src_path: str, 源文件或目录路径，不支持正则表达式；
    :param dst_path: str, 目标字符串路径；
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path)
    check_path_is_exits(src_path)

    if not dst_path.parent.exists():
        dst_path.parent.mkdir(parents=True)

    # 当源对象为文件时
    if src_path.is_file():
        shutil.copy2(str(src_path), str(dst_path))

    # 当源对象为目录时
    if src_path.is_dir():
        if dst_path.exists():
            # 将目录复制到已经存在的目录下
            shutil.copytree(
                str(src_path), str(dst_path / src_path.name), dirs_exist_ok=True
            )
        else:
            # 复制源目标生成指定的新目录
            shutil.copytree(str(src_path), str(dst_path), dirs_exist_ok=True)
            return


def copy_to_target_by_pattern(
    src_path: Union[str, Path],
    dst_path: Union[str, Path],
    recursion: bool = True,
    excludes: str = "",
):
    """通过表达式复制文件或目标到目标路径
    :param src_path: str, 源文件或目录路径，支持正则表达式；
    :param dst_path: str, 目标字符串路径；
    :param recursion: bool, 递归子目录；
    :param excludes: str, 排除表达式，排除单个目录如："x86"，同时排除多个目录用分号分隔如"x86;x64"；
    """
    src_path = str(src_path)
    dst_path = str(dst_path)
    # 两种情况，表达式与绝对路径
    if os.path.exists(src_path):
        # 绝对路径
        pattern = r".+"
    else:
        # 表达式
        last_sep_index = src_path.rfind(os.sep)
        pattern = src_path[last_sep_index + 1 :]
        src_path = src_path[:last_sep_index]
    # 排除项表达式
    if excludes:
        excludes = excludes.split(";")
    else:
        excludes = []

    # 遍历源目录
    for child in os.listdir(src_path):
        # 跳过子目录
        if not recursion and os.path.isdir(src_path + os.sep + child):
            continue

        # 判断是否为排除的项
        is_exclude = False
        for _p in excludes:
            if _p and re.match(_p, child, re.I):
                is_exclude = True
                break
        if is_exclude:
            continue

        # 判断是否为匹配的项
        if re.match(pattern, child, re.I):
            copy_to_target(src_path + os.sep + child, dst_path)


def read_file_stream(file_path: str, start_index, end_index):
    """读取文件流
    :param file_path: str, 文件路径
    :param start_index: int, 读取起始位置
    :param end_index: int, 读取结尾位置
    """
    check_path_is_exits(file_path, path_type="file")
    with open(file_path, mode="rb") as _file:
        _file.seek(start_index)
        return _file.read(end_index - start_index)


def read_file_raw_content(file_path: Union[str, Path], encoding=None) -> tuple:
    """读取文件内容
    :param file_path: 文件路径
    :param encoding: 文件字符编码，没有指定时会按照utf-8，GBK，GB2312，GB18030依次读取
    :return 返回文件类型与读取成功的文件编码
    """
    check_path_is_exits(file_path)
    file_path = Path(file_path)

    if encoding:
        encoding_list = [encoding]
    else:
        encoding_list = ["utf-8", "GBK", "GB2312", "GB18030"]

    error = None
    for encoding in encoding_list:
        try:
            with open(file_path, encoding=encoding) as _file:
                return _file.read(), encoding
        except Exception as e:
            error = e
    else:
        raise error


def read_file_content(
    file_path: Union[Path, str], encoding=None, _return=None, default=None
):
    """读取文件内容
    :param file_path: 文件路径
    :param encoding: 文件字符编码，没有指定时会按照utf-8，GBK，GB2312，GB18030依次读取
    :param _return: 为json时返回json格式数据，否则返回str
    :param default: 文件内容为空时返回的默认值
    :return 返回文件类型与读取成功的文件编码
    """
    if default is None:
        default = {}
    _raw_content, _ = read_file_raw_content(file_path, encoding)
    if _return and _return.lower() == "json":
        _raw_content = _raw_content.strip()
        if _raw_content:
            return json.loads(_raw_content)
        else:
            return default
    else:
        return _raw_content


def save_obj_to_file(obj, file_abs_path: str, exist_ok=True, encoding="utf-8"):
    """保存对象到文件
    :param obj: 待保存对象，仅限文件对象，不能是二进制对象
    :param file_abs_path: 保存路径
    :param exist_ok: 为True时覆盖已经存在的文件，为False时抛错
    :param encoding: 文件编码
    """
    if isinstance(obj, (dict, list, tuple)):
        return save_json_to_file(obj, file_abs_path, exist_ok, encoding)

    if isinstance(obj, bytes):
        obj = obj.decode(encoding)
    else:
        obj = str(obj)

    with open(file_abs_path, mode="w", encoding=encoding) as _file:
        return _file.write(obj)


def save_json_to_file(
    content: dict or list or tuple,
    file_abs_path: Union[Path, str],
    exist_ok=True,
    encoding="utf-8",
    ensure_ascii=False,
    indent=2,
    cls=None,
):
    """将字典、列表、元组保存到文件中
    :param content: 待保存对象，仅限dict,list,tuple
    :param file_abs_path: 保存路径
    :param exist_ok: 为True时覆盖已经存在的文件，为False时抛错
    :param encoding: 文件编码
    :param ensure_ascii:
    :param indent: int, 格式化JSON对象时缩进字符数量
    :param cls: json dumps 的转换类
    """
    file_abs_path = Path(file_abs_path)
    if not exist_ok:
        if file_abs_path.exists():
            raise FileExistsError(f"文件已经存在：{file_abs_path}")

    if not file_abs_path.parent.exists():
        file_abs_path.parent.mkdir(parents=True)

    with open(file_abs_path, mode="w", encoding=encoding) as _file:
        return json.dump(
            content, _file, ensure_ascii=ensure_ascii, indent=indent, cls=cls
        )


def get_newest_file(target: str, _type: str = "c") -> str:
    """获取目录下最新的文件
    :param target: str，目标目录；
    :param _type: str，类型，c按创建时间，m按修改时间，a按访问时间
    """
    if _type.lower() not in ("c", "m", "a"):
        raise ValueError(f"_type参数非法，正确的取值为：a,m,c")
    else:
        _method = getattr(os.path, f"get{_type}time")

    if os.path.isdir(target):
        file_list = os.listdir(target)
        file_list.sort(key=lambda _file: _method(target + os.sep + _file))
        return target + os.sep + file_list[-1]


def get_file_time(file_path: Union[Path, str], _type: str = "c", _return=None):
    """根据文件修改日期获取插件版本号"""
    file_path = Path(file_path)
    if _type.lower() not in ("c", "m", "a"):
        raise ValueError(f"_type参数非法，正确的取值为：a,m,c")
    else:
        _method = getattr(file_path.stat(), f"st_{_type}time")
        _time_obj = datetime.datetime.fromtimestamp(_method)
        if _return == datetime.datetime:
            return _time_obj
        elif _return == datetime.date:
            return _time_obj.date()
        elif _return == float:
            return _time_obj.timestamp()
        elif _return == int:
            return round(_time_obj.timestamp())
        else:
            return _time_obj.strftime("%Y-%m-%d %H:%M:%S")


def get_ini_config_object(config_path: Path):
    """获取config.ini配置文件对象"""
    __config = configparser.ConfigParser()
    __config.read(config_path, encoding="utf-8")
    return __config


def save_ini_config_object(config_path: Path, _object: configparser.ConfigParser):
    """保存配置文件到config.int中"""
    with open(config_path, mode="w", encoding="utf-8") as _file:
        _object.write(_file)
