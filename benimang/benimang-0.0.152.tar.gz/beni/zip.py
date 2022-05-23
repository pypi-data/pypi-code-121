from pathlib import Path
from typing import Callable
from zipfile import ZIP_DEFLATED, ZipFile

import beni


def zipFile(to_file: Path | str, path_dict: dict[str, Path]):
    if type(to_file) is not Path:
        to_file = beni.getPath(to_file)
    beni.makeDir(to_file.parent)
    with ZipFile(to_file, 'w', ZIP_DEFLATED) as f:
        for fname in sorted(path_dict.keys()):
            file = path_dict[fname]
            if file.is_file():
                f.write(file, fname)


def zipFolder(to_file: Path | str, dir: Path, filter_func: Callable[[Path], bool] | None = None):
    ary = beni.listPath(dir, True)
    if filter_func:
        ary = list(filter(filter_func, ary))
    zipFile(to_file, {str(x.relative_to(dir)): x for x in ary})


def extract(file: Path | str, to_dir: Path | str | None = None):
    if type(file) is not Path:
        file = beni.getPath(file)
    to_dir = to_dir or file.parent
    with ZipFile(file) as f:
        for subFile in sorted(f.namelist()):
            try:
                # zipfile 代码中指定了cp437，这里会导致中文乱码
                encodeSubFile = subFile.encode('cp437').decode('gbk')
            except:
                encodeSubFile = subFile
            f.extract(subFile, to_dir)
            # 处理压缩包中的中文文件名在windows下乱码
            if subFile != encodeSubFile:
                toFile = beni.getPath(to_dir, encodeSubFile)
                beni.getPath(to_dir, subFile).rename(toFile)
