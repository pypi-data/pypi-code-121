import hashlib
import json
import mimetypes
import os
import threading
import time
import typing
from dataclasses import dataclass
from pathlib import Path

from queue import Queue, Empty

BUF_SIZE = 4 * 1024 * 1024  # 4MiB
BUF_PRE_FETCH = 64  # 最多消耗 256MiB 额外内存


def cal_hashes(f: typing.IO):
    f.seek(0)

    res = {
        'finish': False,
    }
    queues = {
        'md5': Queue(),
        'sha1': Queue(),
        'sha256': Queue(),
    }

    def _producer(_f: typing.IO):
        while True:
            time.sleep(0.01)
            empty_flag = True

            for _, queue in queues.items():
                if not queue.empty():
                    empty_flag = False
                    break

            if empty_flag:
                count = BUF_PRE_FETCH
                while count > 0:
                    count -= 1
                    content = _f.read(BUF_SIZE)
                    if not content:
                        res['finish'] = True
                        return

                    for _, queue in queues.items():
                        queue.put_nowait(content)

                # 合理的相信算完256M的数据
                # 至少需要这么久
                # 树莓派4： 120MiB/s
                # 8代i5：  370MiB/s
                time.sleep(0.1)

    def _consumer(_algo: str):
        hash_obj = hashlib.new(_algo)
        while True:
            if res['finish'] and queues[_algo].empty():
                break

            try:
                content = queues[_algo].get(timeout=1)
            except Empty:
                continue

            hash_obj.update(content)
            queues[_algo].task_done()

        res[_algo] = hash_obj.hexdigest().upper()

    ths = []
    producer = threading.Thread(target=_producer, args=(f,))
    producer.start()
    ths.append(producer)
    for algorithm in queues.keys():
        consumer = threading.Thread(target=_consumer, args=(algorithm,))
        consumer.start()
        ths.append(consumer)

    for th in ths:
        th.join()

    return res


def cal_sha1_115(f: typing.IO):
    f.seek(0)
    sha1_obj = hashlib.sha1()
    num_bytes = 128 * 1024
    content = f.read(num_bytes)
    if (l := len(content)) < num_bytes:
        content += b'\0' * (num_bytes - l)

    sha1_obj.update(content)
    return sha1_obj.hexdigest().upper()


def cal_md5_baidu(f: typing.IO):
    f.seek(0)
    md5_obj = hashlib.md5()
    num_bytes = 256 * 1024
    content = f.read(num_bytes)
    if (l := len(content)) < num_bytes:
        content += b'\0' * (num_bytes - l)

    md5_obj.update(content)
    return md5_obj.hexdigest().upper()


@dataclass
class MetaNew:
    part: bool = False

    path: Path = None
    raw: typing.IO = None

    # 均为全大写
    size: int = None
    mime: str = None
    md5: str = None
    sha1: str = None
    sha256: str = None

    # 前256K的md5
    md5_baidu: str = None
    # 前128K的sha1
    sha1_115: str = None

    atime: int = None
    mtime: int = None
    ctime: int = None

    @property
    def f(self):
        if self.raw is not None:
            return self.raw

        self.raw = self.path.open('rb')
        stat = self.path.stat()
        self.atime = int(stat.st_atime)
        self.mtime = int(stat.st_mtime)
        self.ctime = int(stat.st_ctime)
        return self.raw

    def cal_part(self) -> bool:
        self.md5_baidu = cal_md5_baidu(self.f)
        self.sha1_115 = cal_sha1_115(self.f)
        self.part = True
        return self.part

    def cal_all(self) -> bool:
        if not self.part:
            self.cal_part()

        hashes = cal_hashes(self.f)
        self.md5 = hashes['md5']
        self.sha1 = hashes['sha1']
        self.sha256 = hashes['sha256']
        return True

    @property
    def mime_type(self) -> str:
        if self.path is not None:
            return mimetypes.guess_type(self.abs_path)[0]

        return 'application/octet-stream'

    @property
    def abs_path(self) -> str:
        return str(self.path.absolute())

    @property
    def basename(self) -> str:
        if self.path is None:
            return 'tmp.txt'

        return self.path.name

    @property
    def suffix(self) -> str:
        return self.path.suffix

    def link_ali(self, name=None) -> str:
        if name is None:
            name = self.basename

        return f"aliyunpan://{name}|{self.sha1}|{self.size}|TMP[Licsber]"

    def link_115(self, name=None) -> str:
        if name is None:
            name = self.basename

        return f"115://{name}|{self.size}|{self.sha1}|{self.sha1_115}"

    def link_baidu(self, name=None) -> str:
        if name is None:
            name = self.basename

        return f"{self.md5}#{self.md5_baidu}#{self.size}#{name}"


class Meta:
    NEED_CHECK = {'size', 'sha1', 'md5', 'sha256', }

    def check(self, other_meta_str: str) -> bool:
        j = json.loads(other_meta_str)
        for check in self.NEED_CHECK:
            if j[check] != self._meta[check]:
                return False

        return True

    def __init__(self, filepath, buf_size=BUF_SIZE):
        abspath = os.path.abspath(filepath)
        if not os.path.exists(abspath):
            print(f"文件不存在 请检查: {abspath}")
            raise FileNotFoundError

        self.buf_size = buf_size

        self._meta = {
            'abspath': abspath,
            'basename': os.path.basename(filepath),
            'size': os.path.getsize(filepath),
            'mime_type': mimetypes.guess_type(abspath)[0],
            'mtime': int(os.path.getmtime(filepath)),
            'md5': '',
            'sha1': '',
            'sha256': '',
            '115_sha1': '',
            'baidu_md5': '',
        }
        self._cal_all()

    @property
    def link_115(self):
        return f"115://{self.basename}|{self.size}|{self.sha1}|{self.head_sha1}"

    @property
    def link_ali(self):
        return f"aliyunpan://{self.basename}|{self.sha1}|{self.size}|TMP[Licsber]"

    @property
    def link_baidu(self):
        return f"{self.md5}#{self.head_md5}#{self.size}#{self.basename}"

    @property
    def link_licsber(self):
        return f"licsber://{self.sha256}-{self.sha1}-{self.size}-{self.basename}"

    @property
    def csv_header(self):
        return 'Key,Filename,Size,SHA1,HeadSHA1,MD5,HeadMD5\n'

    @property
    def csv(self):
        res = self.csv_header
        res += f"Value,{self.basename},{self.size},{self.sha1},{self.head_sha1},{self.md5},{self.head_md5}\n"
        res += f",,,,,,{self.link_115}\n"
        res += f",,,,,,{self.link_ali}\n"
        res += f",,,,,,{self.link_baidu}"
        return res

    def save_meta_csv(self):
        with open(self.abspath + '.licsber.csv', 'w') as f:
            f.write(self.csv)

    def __str__(self):
        res = self._meta.copy()
        del res['abspath']
        res.update({
            'link_115': self.link_115,
            'link_ali': self.link_ali,
            'link_baidu': self.link_baidu,
            'link_licsber': self.link_licsber,
        })
        return json.dumps(res, ensure_ascii=False)

    @property
    def abspath(self):
        return self._meta['abspath']

    @property
    def basename(self):
        return self._meta['basename']

    @property
    def size(self):
        return self._meta['size']

    @property
    def mtime(self):
        return self._meta['mtime']

    @property
    def mime_type(self):
        return self._meta['mime_type']

    @property
    def md5(self):
        return self._meta['md5']

    @property
    def sha1(self):
        return self._meta['sha1']

    @property
    def sha256(self):
        return self._meta['sha256']

    @property
    def head_sha1(self):
        return self._meta['115_sha1']

    @property
    def head_md5(self):
        return self._meta['baidu_md5']

    def _cal_all(self):
        with open(self.abspath, 'rb') as f:
            self._meta['115_sha1'] = cal_sha1_115(f)
            self._meta['baidu_md5'] = cal_md5_baidu(f)
            hashes = cal_hashes(f)
            self._meta['md5'] = hashes['md5']
            self._meta['sha1'] = hashes['sha1']
            self._meta['sha256'] = hashes['sha256']


if __name__ == '__main__':
    test_path = '/tmp/test.licsber'
    with open(test_path, 'w') as _f:
        _f.write('Hello Licsber.')

    meta = Meta(test_path)
    meta.save_meta_csv()
    print(meta, end='')
    # noinspection SpellCheckingInspection
    assert meta.link_115 == '115://test.licsber|14|02B02681636CCEDB820385C8A87EA2E1E18ACD5C' \
                            '|C24486ADE0E6AAE9376E4994A7A1267277A13295'
