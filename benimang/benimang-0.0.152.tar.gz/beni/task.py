from contextlib import asynccontextmanager
from datetime import datetime as Datetime
from pathlib import Path
from typing import Final
from uuid import uuid4

import nest_asyncio
import typer
from colorama import Back, Fore

import beni
import beni.log as blog
import beni.color as bprint

_startTime: Datetime | None = None
_logFile: Path | None = None

_HOLD_LOGFILE_COUNT = 100

nest_asyncio.apply()
app: Final = typer.Typer()


@asynccontextmanager
async def task():
    global _startTime
    _startTime = Datetime.now()
    beni.initErrorFormat()
    try:
        blog.init(logFile=_logFile)
        yield
    except BaseException as ex:
        bprint.set(Fore.LIGHTRED_EX)
        blog.error(str(ex))
        blog.error('执行失败')
        raise
    finally:

        if blog.getCountCritical():
            color = Fore.LIGHTWHITE_EX + Back.LIGHTMAGENTA_EX
        elif blog.getCountError():
            color = Fore.LIGHTWHITE_EX + Back.LIGHTRED_EX
        elif blog.getCountWarning():
            color = Fore.BLACK + Back.YELLOW
        else:
            color = Fore.BLACK + Back.LIGHTGREEN_EX

        bprint.set(color)
        blog.info('-' * 75)

        msgAry = ['任务结束']
        if blog.getCountCritical():
            msgAry.append(f'critical({blog.getCountCritical()})')
        if blog.getCountError():
            msgAry.append(f'error({blog.getCountError()})')
        if blog.getCountWarning():
            msgAry.append(f'warning({blog.getCountWarning()})')

        bprint.set(color)
        blog.info(' '.join(msgAry))

        passTime = str(Datetime.now() - _startTime)
        if passTime.startswith('0:'):
            passTime = '0' + passTime
        blog.info(f'用时: {passTime}')

        # 删除多余的日志
        try:
            if _logFile:
                logfile_list = list(_logFile.parent.glob('*.log'))
                logfile_list.remove(_logFile)
                logfile_list.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                logfile_list = logfile_list[_HOLD_LOGFILE_COUNT:]
                for logfile in logfile_list:
                    beni.remove(logfile)
        except:
            pass


def setLogPath(logpath: Path):
    if _startTime:
        blog.warning('task.setLogDir 必须在任务启动前调用，本次忽略执行')
    else:
        global _logFile
        _logFile = beni.getPath(logpath, f'{uuid4()}.log')


def appRun():
    '''捕捉正常退出的异常不向外抛出'''
    try:
        app()
    except BaseException as ex:
        if type(ex) is SystemExit and ex.code == 0:
            # 正常结束
            pass
        else:
            raise


# @task()
# async def debug(*args: str):
#     from typer.testing import CliRunner
#     CliRunner().invoke(app, args)
