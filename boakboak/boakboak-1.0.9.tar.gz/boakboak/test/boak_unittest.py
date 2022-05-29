# test_unittest.py

import logging
from datetime import datetime as dt
import os, re, sys
import subprocess

import boakboak.src.settings as sts


class UnitTestWithLogging:
    def __init__(self):
        self.timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))
        self.logDir = os.path.join(sts.testPath, "logs")
        assert os.path.isdir(self.logDir), f"logDir: {self.logDir} does not exist !"
        self.logDefaultName = f"{os.path.basename(__file__)[:-3]}_{self.timeStamp}.log"

    def mk_logger(self, *args, **kwargs):
        # logging config to put somewhere before calling functions
        # call like: logger.debug(f"logtext: {anyvar}")
        logger = logging.getLogger(os.sep.join(__name__))
        logger.setLevel(logging.INFO)
        logformat = "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s"
        datefmt = "%m-%d %H:%M"
        logForm = logging.Formatter(
            fmt=logformat, datefmt=datefmt
        )  # logging here refers to the logDir
        logPath = os.path.join(self.logDir, self.logDefaultName)
        logHandler = logging.FileHandler(logPath, mode="a")
        logHandler.setFormatter(logForm)
        logger.addHandler(logHandler)
        return logger

    def main(self, *args, **kwargs):
        logger = self.mk_logger(*args, **kwargs)
        with sts.temp_chdir(sts.appBasePath):
            cmds = ["python", "-m", "unittest"]
            results = (
                subprocess.Popen(cmds, stderr=subprocess.PIPE, executable=sys.executable)
                .stderr.read()
                .decode("utf-8")
            )
            results = "\n".join(
                [l for l in results.replace("\r", "").replace("\n\n", "\n").split("\n")]
            )
            logger.info(f"\n{results}")
            for l in results.split("\n"):
                print(l)


if __name__ == "__main__":
    UnitTestWithLogging().main()
