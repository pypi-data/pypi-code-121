import logging
import subprocess
from typing import List

from peek_platform.WindowsPatch import isWindows
from peek_platform.util.PtyUtil import PtyOutParser, spawnPty, logSpawnException

logger = logging.getLogger(__name__)

NG_BUILD_ARGS = "ng build --prod --optimization  --common-chunk --vendor-chunk".split()


def runDocBuild(feBuildDir: str):
    if isWindows:
        return __runNodeCmdWin(feBuildDir, ["bash", "./build_html_docs.sh"])
    return __runNodeCmdLin(feBuildDir, ["bash", "./build_html_docs.sh"])


def runNgBuild(feBuildDir: str):
    if isWindows:
        return __runNodeCmdWin(feBuildDir, NG_BUILD_ARGS)
    return __runNodeCmdLin(feBuildDir, NG_BUILD_ARGS)


def runTsc(feDir: str):
    if isWindows:
        return __runNodeCmdWin(feDir, ["tsc"])
    return __runNodeCmdLin(feDir, ["tsc"])


def __runNodeCmdWin(feBuildDir: str, cmds: List[str]):
    proc = subprocess.Popen(
        cmds, cwd=feBuildDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )

    logger.info("Wating up to 5m for command to finish")
    outs, errs = proc.communicate(timeout=300)

    if proc.returncode in (0,):
        logger.info("%s finished successfully" % " ".join(cmds))
        # for line in (outs + errs).decode().splitlines():
        #     print(".")
    else:
        for line in (outs + errs).decode().splitlines():
            print(line)

        raise Exception("%s in %s failed" % (" ".join(cmds), feBuildDir))

    logger.info("Command complete")


def __runNodeCmdLin(feBuildDir: str, cmds: List[str]):
    try:
        parser = PtyOutParser(loggingStartMarker="Hash: ")
        spawnPty("cd %s && %s" % (feBuildDir, " ".join(cmds)), parser)

    except Exception as e:
        logSpawnException(e)
        raise
