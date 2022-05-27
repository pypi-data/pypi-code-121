import json
import re
import subprocess
from datetime import date, timedelta
from hashlib import md5
from typing import Union

import loguru
from apscheduler.triggers.cron import CronTrigger

from duyan_download_task import constants


def is_json(string: Union[str, bytes, bytearray]) -> bool:
    """
    判断是否是json字符串
    :param string:
    :return:
    """
    try:
        json.loads(string)
        return True
    except Exception:
        return False


def load_json(json_str: Union[str, bytes, bytearray]) -> dict or None:
    """
    json字符串转dict
    :param json_str:
    :return:
    """
    if is_json(json_str):
        return json.loads(json_str, encoding=constants.UTF8)
    return None


def dump_json(obj) -> str:
    """
    object转json字符串
    :param obj:
    :return:
    """
    return json.dumps(obj, ensure_ascii=False)


def get_date_around_today(days: int, origin_date: date) -> date:
    delta = timedelta(days=days)
    return origin_date + delta


def get_file_md5(file_path: str):
    try:
        with open(file_path, 'rb') as file_obj:
            digest = md5()
            digest.update(file_obj.read())
            md5_hex = digest.hexdigest()
            return md5_hex
    except Exception as e:
        return ""


def get_file_md5_sub(file_path):
    try:
        child = subprocess.Popen([f"md5sum {file_path}"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        md5val = child.stdout.read()
        return md5val and str(md5val, "utf-8").split(" ")[0] or "NULL"
    except Exception as e:
        return "NULL"


def get_bytes_md5(data: bytes):
    try:
        digest = md5()
        digest.update(data)
        md5_hex = digest.hexdigest()
        return md5_hex
    except Exception as e:
        return ""


def get_communicate_error_result(res):
    if len(res) < 1:
        return None
    if res[1] is not None and res[1] != "" and res[1] != '':
        messge = res[1]
        if isinstance(messge, bytes):
            return str(messge, encoding="utf-8").replace("\n", "")
        else:
            return str(messge).replace("\n", "")
    return None


def get_cron_trigger_for_str(cron):
    pattern = re.compile(r'\s+')
    corn_arr = re.split(pattern, cron)
    if corn_arr is None or len(corn_arr) != 6:
        message = "cron 表达式格式错误!"
        loguru.logger.error(message)
        raise Exception(message)
    return CronTrigger(second=corn_arr[0], minute=corn_arr[1], hour=corn_arr[2], day=corn_arr[3],
                       month=corn_arr[4], year=corn_arr[5])
