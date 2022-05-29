import hashlib
import json
import os
from pathlib import Path

import tqdm

from licsber.utils.ufile import fun_check_path_exist, save_file
from licsber.utils.umeta import Meta
from licsber.utils.utime import cal_time


@cal_time(output=True)
@fun_check_path_exist(clean=True)
def save_115_dir(start_path=None):
    if os.path.isfile(start_path):
        meta = Meta(start_path)
        print(str(meta))

        save_path = start_path + '.json'
        if not os.path.exists(save_path):
            with open(save_path, 'w') as f:
                f.write(str(meta))
                return

        print('.json文件已存在 开始校验.')
        with open(save_path) as f:
            if meta.check(f.read()):
                print('校验通过.')
            else:
                print('校验失败.')
                with open(start_path + '.new.json', 'w') as f:
                    f.write(str(meta))

        return

    if not os.path.isdir(start_path):
        print(f"选定目录错误: {start_path}")
        return

    def fun_sha1(content):
        sha1_obj = hashlib.sha1()
        sha1_obj.update(content)
        return sha1_obj.hexdigest().upper()

    start_path = Path(start_path)
    save_json_name = 'licsber-bak.json'
    save_path = start_path / save_json_name
    old_path = start_path / 'licsber-bak-old.json'

    exist_sha1 = ''
    if save_path.exists():
        print(f"已存在归档文件: {save_path}")
        exist_sha1 = fun_sha1(save_path.open('rb').read())
        print(f"归档文件sha1: {exist_sha1}")
        os.rename(save_path, old_path)

    def build(root):
        node = {
            'dir_name': os.path.basename(root),
            'dirs': [],
            'files': [],
            'baidu': [],
            'licsber': [],
        }
        all_files = list(os.listdir(root))
        all_files.sort()
        with tqdm.tqdm(total=len(all_files)) as t:
            for i in all_files:
                t.update()
                path = os.path.join(root, i)
                if os.path.isdir(path):
                    # 去除威联通QNAP-NAS中的缓存文件夹
                    if os.path.basename(path) in {'.@__thumb', '@Recycle', '@Transcode', 'licsber-bak'}:
                        continue

                    exists_path = os.path.join(path, save_json_name)
                    if os.path.exists(exists_path):
                        info = json.load(open(exists_path))
                    else:
                        info = build(path)

                    node['dirs'].extend([info])
                elif os.path.isfile(path):
                    if os.path.basename(path) in {save_json_name, 'licsber-bak-old.json'}:
                        continue

                    meta = Meta(path)
                    node['files'].append(meta.link_115.replace('115://', '', 1))
                    node['baidu'].append(meta.link_baidu)
                    node['licsber'].append(meta.link_licsber)

        return node

    res = build(start_path)
    dir_info = json.dumps(res)
    sha1 = fun_sha1(dir_info.encode())
    print(f"归档文件sha1: {sha1}")
    if exist_sha1 and exist_sha1 == sha1:
        print('校验通过.')
        os.remove(old_path)

    save_file(start_path, save_json_name, dir_info)
