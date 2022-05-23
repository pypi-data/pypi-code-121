import asyncio

import beni
import beni.byte as bbyte


async def executeWinscp(winscp_exe: str, key_file: str, server: str, cmd_list: list[str], show_cmd: bool = True):
    logFile = beni.getPathUser('executeWinScp.log')
    beni.remove(logFile)
    ary = [
        'option batch abort',
        'option transfer binary',
        f'open sftp://{server} -privatekey={key_file} -hostkey=*',
    ]
    ary += cmd_list
    ary += [
        'close',
        'exit',
    ]
    # /console
    cmd = f'{winscp_exe} /log={logFile} /loglevel=0 /command ' + ' '.join("%s" % x for x in ary)
    return await execute(cmd)


async def executeTry(*args: str, output: str = '', error: str = ''):
    _, outputBytes, errorBytes = await execute(*args)
    if output and output not in bbyte.decode(outputBytes):
        raise Exception(f'命令执行失败: {" ".join(args)}')
    if error and error not in bbyte.decode(errorBytes):
        raise Exception(f'命令执行失败: {" ".join(args)}')


async def execute(*args: str):
    proc = await asyncio.create_subprocess_shell(
        ' '.join(args),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout, stderr


# -------------------------------------------------------

# def execute(*pars: str, show_cmd: bool = True, show_output: bool = False, ignore_error: bool = False):
#     cmd = ' '.join(pars)
#     if show_cmd:
#         info(cmd)
#     p = subprocess.Popen(
#         cmd,
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     outBytes, errBytes = p.communicate()
#     p.kill()
#     if show_output:
#         outStr = decode(outBytes).replace('\r\n', '\n')
#         errStr = decode(errBytes).replace('\r\n', '\n')
#         if outStr:
#             info(f'output:\n{outStr}')
#         if errStr:
#             info(f'error:\n{errStr}')
#     if not ignore_error and p.returncode != 0:
#         raise Exception('执行命令出错')
#     return p.returncode, outBytes, errBytes
