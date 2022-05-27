"""samba操作工具模块
包含功能：
1.获取服务器连接句柄；
2.创建目录；
3.上传文件；
"""
# coding = utf-8
import os
import json
import time
import logging
from pathlib import Path
from typing import Union
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

from .encrypt import to_decode
from .file import check_path_is_exits


__all__ = ["get_server_handler", "create_directory", "upload_file", "COM_SAMBA", "TEST_SAMBA"]

IP_ADDRESS = None
USERNAME = None
PASSWORD = None

COM_SAMBA: dict = json.loads(to_decode(os.environ["COM_SAMBA"]))
TEST_SAMBA: dict = json.loads(to_decode(os.environ["TEST_SAMBA"]))

logger = logging.getLogger("DengUtils")


def get_server_handler(
    username=COM_SAMBA["username"],
    password=COM_SAMBA["password"],
    my_name=COM_SAMBA["my_name"],
    remote_name=COM_SAMBA["remote_name"],
    ip_address=COM_SAMBA["ip_address"],
):
    """获取服务器连接句柄"""
    conn = SMBConnection(
        username=username, password=password, my_name=my_name, remote_name=remote_name,
    )
    conn.connect(ip=ip_address)
    global IP_ADDRESS, USERNAME, PASSWORD
    IP_ADDRESS = ip_address
    USERNAME = username
    PASSWORD = password
    return conn


def get_server2_handler(
    username=TEST_SAMBA["username"],
    password=TEST_SAMBA["password"],
    my_name=TEST_SAMBA["my_name"],
    remote_name=TEST_SAMBA["remote_name"],
    ip_address=TEST_SAMBA["ip_address"],
):
    """获取服务器连接句柄"""
    conn = SMBConnection(
        username=username, password=password, my_name=my_name, remote_name=remote_name,
    )
    conn.connect(ip=ip_address)
    global IP_ADDRESS, USERNAME, PASSWORD
    IP_ADDRESS = ip_address
    USERNAME = username
    PASSWORD = password
    return conn


def create_directory(
    conn: SMBConnection, service_name: str, path: str, is_exist_ok=True
) -> bool:
    """创建目录，支持递归创建"""
    last_result = None
    dir_list = list(Path(path).parents)
    # 丢弃已经存在的根目录
    dir_list.pop()
    # 将目录本身插入
    dir_list.insert(0, Path(path))
    while dir_list:
        _path = dir_list.pop()
        try:
            conn.createDirectory(service_name=service_name, path=str(_path))
        except Exception as e:
            last_result = False
            if not is_exist_ok:
                raise e
        else:
            last_result = True
    return last_result


def upload_file(conn: SMBConnection, service_name: str, path: str, file_path: Union[str, Path]):
    logger.info(f"推送文件：{file_path} => {path}")
    # 防止多个终端同时推送同一个文件到同一地址导致的冲突
    # 重试30次，都失败时抛错
    count = 30
    while True:
        with open(file_path, "rb") as _file_obj:
            try:
                conn.storeFile(service_name=service_name, path=path, file_obj=_file_obj)
            except OperationFailure:
                count -= 1
                if count > 0:
                    logger.warning(f"上传文件失败：{path}，一秒后重试")
                    time.sleep(1)
                else:
                    raise
            else:
                break


def download_file(conn: SMBConnection, service_name: str, path: str, file_path: Union[str, Path]):
    with open(file_path, mode="wb") as _file:
        file_size = conn.retrieveFile(service_name, path, _file)
    logger.info(f"文件下载完成：大小{file_size}, {service_name}{path} => {file_path}")


def delete_file(conn: SMBConnection, service_name: str, path_file_pattern: str):
    _file_abs_path = f"{service_name}/{path_file_pattern}"
    try:
        conn.deleteFiles(service_name, path_file_pattern)
    except Exception as e:
        logger.warning(f"删除文件失败，文件不存在：{_file_abs_path}")
    else:
        logger.info(f"删除文件成功：{_file_abs_path}")


def pull_file_by_samba(file_path: Path, target_dir: str):
    """从samba服务器上下载文件
    :param file_path: Path,下载文件保存绝对路径
    :param target_dir: str,samba服务器上存储备份文件目录的相对地址
    """
    # samba服务上共享节点目录
    service_name = "share"
    # 连接仓库samba服务器
    conn = get_server_handler()
    # 下载文件
    target_file = target_dir + "/" + file_path.name
    download_file(conn, service_name, target_file, file_path)
    logger.info(f"文件下载成功：{service_name}{target_dir}=>{file_path}")


def push_file_to_samba(file_path: Path, target_dir: str):
    """推送文件到samba服务器上
    :param file_path: Path,本地文件绝对路径
    :param target_dir: str,samba服务器上存储备份文件目录的相对地址
    """
    global IP_ADDRESS
    check_path_is_exits(file_path, path_type="file")
    file_name = file_path.name
    # samba服务上共享节点目录
    service_name = "share"
    # 连接仓库samba服务器
    conn = get_server_handler()
    # 创建目录
    create_directory(conn, service_name, target_dir)
    # 上传新包
    upload_file(conn, service_name, f"{target_dir}/{file_name}", file_path)
    # 仓库完整路径
    package_repo_abs_path = (
        f"/{IP_ADDRESS}/{service_name}{target_dir}/{file_name}"
    )
    logger.info(f"备份成功：{file_path.stem}=>{package_repo_abs_path}")


if __name__ == "__main__":
    pass
