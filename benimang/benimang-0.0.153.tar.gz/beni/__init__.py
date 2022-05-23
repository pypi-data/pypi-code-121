import asyncio
import os
import random
import shutil
from contextlib import asynccontextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Coroutine, TypeVar, cast

Fun = TypeVar("Fun", bound=Callable[..., object])
AsyncFun = TypeVar("AsyncFun", bound=Callable[..., Coroutine[Any, Any, object]])
AnyType = TypeVar("AnyType")


def getPath(path: str | Path, expand: str = ''):
    if type(path) is not Path:
        path = Path(path)
    return path.joinpath(expand).resolve()


def getPathUser(expand: str = ''):
    return getPath(Path('~').expanduser(), expand)


def getPathWorkspace(expand: str = ''):
    return getPathUser(f'beni.workspace/{expand}')


def getPathDesktop(expand: str = ''):
    return getPathUser(f'Desktop/{expand}')


def openWinDir(dir: Path | str):
    os.system(f'start explorer {dir}')


def remove(path: Path | str):
    if type(path) is not Path:
        path = getPath(path)
    if path.is_file():
        path.unlink(True)
    elif path.is_dir():
        shutil.rmtree(path)


def makeDir(path: Path | str):
    if type(path) is not Path:
        path = getPath(path)
    path.mkdir(parents=True, exist_ok=True)


def clearDir(dir: Path):
    for sub in dir.iterdir():
        remove(sub)


def copy(src: Path | str, dst: Path | str):
    if type(src) is not Path:
        src = getPath(src)
    if type(dst) is not Path:
        dst = getPath(dst)
    makeDir(dst.parent)
    if src.is_file():
        shutil.copyfile(src, dst)
    elif src.is_dir():
        shutil.copytree(src, dst)
    else:
        if not src.exists():
            raise Exception(f'copy error: src not exists {src}')
        else:
            raise Exception(f'copy error: src not support {src}')


def move(src: Path | str, dst: Path | str, force: bool = False):
    if type(src) is not Path:
        src = getPath(src)
    if type(dst) is not Path:
        dst = getPath(dst)
    if dst.exists():
        if force:
            remove(dst)
        else:
            raise Exception(f'move error: dst exists {dst}')
    makeDir(dst.parent)
    os.rename(src, dst)


def jsonDumpsMini(value: Any):
    import json
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def listPath(path: Path | str, recursive: bool = False):
    '''获取指定路径下文件以及目录列表'''
    if type(path) is not Path:
        path = getPath(path)
    if recursive:
        return list(path.glob('**/*'))
    else:
        return list(path.glob("*"))


def listFile(path: Path | str, recursive: bool = False):
    '''获取指定路径下文件列表'''
    if type(path) is not Path:
        path = getPath(path)
    if recursive:
        return list(filter(lambda x: x.is_file(), path.glob('**/*')))
    else:
        return list(filter(lambda x: x.is_file(), path.glob('*')))


def listDir(path: Path | str, recursive: bool = False):
    '''获取指定路径下目录列表'''
    if type(path) is not Path:
        path = getPath(path)
    if recursive:
        return list(filter(lambda x: x.is_dir(), path.glob('**/*')))
    else:
        return list(filter(lambda x: x.is_dir(), path.glob('*')))


def md5Bytes(data: bytes):
    import hashlib
    return hashlib.md5(data).hexdigest()


def md5Str(content: str):
    return md5Bytes(content.encode())


def md5Data(data: Any):
    return md5Str(
        jsonDumpsMini(data)
    )


def crcBytes(data: bytes):
    import binascii
    return hex(binascii.crc32(data))[2:].zfill(8)


def crcStr(content: str):
    return crcBytes(content.encode())


def crcData(data: Any):
    return crcStr(
        jsonDumpsMini(data)
    )


def retry(times: int):
    def fun(func: AsyncFun) -> AsyncFun:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            current = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except:
                    current += 1
                    if current >= times:
                        raise
        return cast(AsyncFun, wrapper)
    return fun


@asynccontextmanager
async def timeout(timeout: float):
    import async_timeout
    async with async_timeout.timeout(timeout):
        yield


def asyncRun(coroutine: Coroutine[Any, Any, AnyType]) -> AnyType:
    # 避免出现 RuntimeError: Event loop is closed
    # asyncio.get_event_loop().run_until_complete(coroutine)
    import nest_asyncio
    nest_asyncio.apply()
    return asyncio.run(coroutine)


def hold(msg: str | None = None, password: bool = False, *exitvalue_list: str):
    msg = msg or '测试暂停，输入exit可以退出'
    exitvalue_list = exitvalue_list or ('exit',)
    import getpass
    inputFunc = password and getpass.getpass or input
    while True:
        inputValue = inputFunc(f'{msg}: ')
        if (inputValue in exitvalue_list) or ('*' in exitvalue_list):
            return inputValue


IntFloatStr = TypeVar("IntFloatStr", int, float, str)


def toFloat(value: IntFloatStr, default: float = 0):
    result = default
    try:
        result = float(value)
    except:
        pass
    return result


def toInt(value: IntFloatStr, default: int = 0):
    result = default
    try:
        result = int(value)
    except:
        pass
    return result


def getValueInside(value: IntFloatStr, minValue: IntFloatStr, maxValue: IntFloatStr):
    '包括最小值和最大值'
    value = min(value, maxValue)
    value = max(value, minValue)
    return value


def initErrorFormat():
    import pretty_errors
    pretty_errors.configure(
        separator_character='*',
        filename_display=pretty_errors.FILENAME_COMPACT,
        # line_number_first   = True,
        display_link=True,
        lines_before=5,
        lines_after=2,
        line_color=pretty_errors.RED + '> ' + pretty_errors.default_config.line_color,
        code_color='  ' + pretty_errors.default_config.line_color,
        truncate_code=False,
        display_locals=True
    )
    # pretty_errors.blacklist('c:/python')


def goAhead(msg: str = '确认'):
    code = str(random.randint(1000, 9999))
    hold(f'{msg} [ {code} ]', False, code)


def Counter(value: int = 0):
    def _(v: int = 1):
        nonlocal value
        value += v
        return value
    return _


def inputx(msg: str, check: Callable[[str], Any]):
    while True:
        try:
            value = input(f'{msg}')
            if check(value):
                return value
        except:
            pass
