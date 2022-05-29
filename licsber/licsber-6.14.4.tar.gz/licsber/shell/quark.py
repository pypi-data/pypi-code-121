import os.path

from licsber.drive.quark import Quark
from licsber.utils.ufile import fun_check_path_exist
from licsber.utils.utime import cal_time


@cal_time(output=True)
@fun_check_path_exist(clean=False)
def upload_by_licsber_json(start_path: str = None):
    if not os.path.isfile(start_path):
        print("[ERROR] The path is not a file.")
        return

    quark = Quark()
    if start_path.endswith('.json'):
        suc = quark.quick_upload_licsber_json(start_path)
    else:
        print(f"[ERROR] The file {start_path} is not a licsber json file.")
        return False

    if suc:
        print("[SUCCESS] Upload success.")
    else:
        print("[ERROR] Upload failed.")
