# standard lib imports
import colorama as color

color.init()
import datetime as dt
from collections import defaultdict
import os, re, sys, time
import unittest

# test package imports
import boakboak.src.settings as sts
import boakboak.src.params as params

import subprocess

subprocess.call(["black", sts.appBasePath], shell=False)

# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.timeStamp = re.sub(r"([:. ])", r"-", str(dt.datetime.now()))
        cls.logPath = os.path.join(sts.testPath, "logs")
        cls.logDefault = f"{__file__[:-3]}_{cls.timeStamp}.log"
        assert os.path.isdir(
            cls.logPath
        ), f"LogPath: {cls.logPath} does not exist !"
        cls.testResults = defaultdict(list)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        try:
            cls.write_log_file(*args, **kwargs)
        except Exception as e:
            print(f"UnitTest, tearDownClass, e: {e}")

    @classmethod
    def write_log_file(cls, *args, **kwargs):
        """
        takes the logfile produced by previous test by taking the most recent log file
        adds test results from this cls to log file
        """
        if cls.verbose >= 1:
            print(f"\twaiting 1 for sublime logFile to be written: ...")
        time.sleep(1)
        if logFile := sorted(os.listdir(cls.logPath), reverse=False):
            logFile = logFile[-1]
        else:
            logFile = cls.logDefault
        if cls.verbose >= 1:
            print(f"\tlogFile: {logFile}")
        with open(os.path.join(cls.logPath, logFile), "a") as f:
            outs = [
                f"\n\t{i}  {k}: {vs}"
                for i, (k, vs) in enumerate(cls.testResults.items())
            ]
            f.write(f"\n\n{cls.timeStamp}:")
            for out in outs:
                f.write(out)

    def test_get_params(self, *args, name="test_get_params", **kwargs):
        if self.verbose >= 1:
            print(f"{name = }")
        ############ read from file #################
        expected = "TestBoakboak"

        # run test
        pars = params.Params().get_params(*args, apps=["testing"], **kwargs)

        # assert test results
        successful = pars["testing"].get("name") == expected
        if not successful:
            msg = f"assertEqual({pars['testing'].get('name')}, {expected}) = {successful}"
            self.testResults[name].append(msg)
            # printing test results
            if self.verbose >= 1:
                print(f"\t{msg = }")
        self.assertEqual(pars["testing"].get("name"), expected)

        ############ derrive from location #################
        # in this case the app does not not exist in /apps instead a directory boakboak exists
        # therefore params has to return the content of packages/boakboak/boakboak.yml
        app = "boakboak"
        expected = "TestBoakboak"

        # run test
        pars = params.Params().get_params(*args, apps=[app], **kwargs)[app][
            "name"
        ]

        # assert test results
        successful = pars == expected
        if not successful:
            msg = f"assertEqual({pars}, {expected}) = {successful}"
            self.testResults[name].append(msg)
            # printing test results
            if self.verbose >= 1:
                print(f"\t{msg = }")
        self.assertEqual(pars, expected)

    def test_find_app_path(self, *args, name="test_find_app_path", **kwargs):
        if self.verbose >= 1:
            print(f"{name = }")
        app = "boakboak"
        expectedPath, expectedName = "C:/python_venvs/packages/boakboak", app

        # run test
        paramsPath, defaultName = params.Params().find_app_path(
            app, *args, **kwargs
        )

        # assert name
        successful = paramsPath == expectedPath
        if not successful:
            msg = f"assertEqual({paramsPath}, {expectedPath}) = {successful}"
            self.testResults[name].append(msg)
            # printing test results
            if self.verbose >= 1:
                print(f"\t{msg = }")
        self.assertEqual(
            sts.os_sep_adj(paramsPath), sts.os_sep_adj(expectedPath)
        )

        # assert paramsPath
        successful = defaultName = expectedName
        if not successful:
            msg = f"assertEqual({defaultName}, {expectedName}) = {successful}"
            self.testResults[name].append(msg)
            # printing test results
            if self.verbose >= 1:
                print(f"\t{msg = }")
        self.assertEqual(defaultName, expectedName)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
