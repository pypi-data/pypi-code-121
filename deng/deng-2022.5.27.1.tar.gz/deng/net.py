import re
import socket
import logging
import requests
from typing import Union
from pathlib import Path
from contextlib import closing
from urllib.parse import urlparse

from . import file as file_utils
from . import encrypt as encrypt_utils


logger = logging.getLogger("DengUtils")


def get_host_ip(reference: str = "") -> str:
    """获取主机ip地址
    :param reference: str, 参考地址，本地可能存在多个IP，获取能够访问此地址的IP
    """
    # 支持http或https地址，从中提取域名/主机地址
    absolute_http_url_regexp = re.compile(r"^https?://", re.I)
    if absolute_http_url_regexp.match(reference):
        url_obj = urlparse(reference)
        reference = url_obj.netloc

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((reference if reference else "114.114.114.114", 80))
        ip = s.getsockname()[0]
        logger.debug(f"获取本机IP地址成功：{ip}")
    except Exception as e:
        logger.debug(e)
        logger.warning(f"获取本机IP地址失败")
        ip = ""
    finally:
        s.close()
    return ip


def is_valid_ip(ip):
    """Returns true if the given string is a well-formed IP address.
    Supports IPv4 and IPv6.
    """
    # IP地址必须是字符串
    if not isinstance(ip, str):
        return False

    if not ip or "\x00" in ip:
        # getaddrinfo resolves empty strings to localhost, and truncates
        # on zero bytes.
        return False

    try:
        res = socket.getaddrinfo(
            ip, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_NUMERICHOST
        )
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise


def verify_download_url(url: str, timeout=3):
    """校验URL下载地址是否存在"""
    try:
        res = requests.head(url, timeout=timeout)
    except Exception as e:
        return False
    else:
        if res.status_code < 400:
            return True
        else:
            return False


def download_file(url: str, file_save_path: Path):
    """下载文件"""
    # 检查存储文件夹是否存在，不存在时创建
    if not file_save_path.parent.exists():
        file_save_path.parent.mkdir(parents=True)
    # 覆盖提醒
    if file_save_path.exists():
        logger.warning(f"目标文件已经存在，直接覆盖！")
    # 开始下载
    with closing(requests.get(url, stream=True)) as _res:
        with open(file_save_path, mode="wb") as _app:
            for chunk in _res.iter_content(chunk_size=10 * 1024 * 1024):
                if chunk:
                    _app.write(chunk)
    # 检查下载结果
    if file_save_path.exists():
        logger.info(f"下载成功，保存路径：{file_save_path}")
        return True
    else:
        raise FileNotFoundError(f"下载失败：{url}")


def download_and_check_md5(url: str, target: Union[str, Path], md5: str = ""):
    """下载文件"""
    target = Path(target) if not isinstance(target, Path) else target

    # 检查需要下载的文件是否已经存在，如果存在且md5相同则直接使用
    if target.exists():
        if md5 and encrypt_utils.md5sum(_file_path=target) == md5:
            logger.info(f"本地已经存在目标文件，且md5校验通过，跳过下载：{target}")
            return
        target.unlink(missing_ok=True)

    # 检查下载目标存储路径是否存在，不存在时创建，防止后续报错
    if not target.parent.exists():
        target.parent.mkdir(parents=True)

    logger.debug(f"开始下载文件：{url}=>{target}")
    res = requests.get(url, stream=True)
    with open(target, mode="wb") as file:
        for packet in res.iter_content(chunk_size=5 * 1024 * 1024):
            if packet:
                file.write(packet)
    if md5:
        assert encrypt_utils.md5sum(_file_path=target) == md5
        logger.info(f"下载完成且md5校验通过：{target}")
        return
    file_utils.check_path_is_exits(target, path_type="file")
    logger.info(f"下载完成，跳过md5：{target}")
