#cheese

import os
import sys
import time

from Cheese.resourceManager import ResMan
from Cheese.Logger import Logger
from Cheese.metadata import Metadata
from Cheese.ErrorCodes import Error
from Cheese.testError import *
from Cheese.cheeseRepository import CheeseRepository
from Cheese.mockManager import MockManager

class CheeseTests:

    @staticmethod
    def testAll():
        CheeseTests.testTotalCount = 0
        CheeseTests.testErrorCount = 0
        CheeseTests.testFailCount = 0
        CheeseTests.testOkCount = 0
        CheeseTests.testIgnoredCount = 0

        CheeseTests.mocks = {}
        CheeseRepository.startTesting(MockManager)

        for testKey in Metadata.tests.keys():
            test = Metadata.tests[testKey]
            
            testFile = os.path.join(ResMan.root(), *test["FILE"].split("/")) + ".py"
            testHeader = f"""
Running {CheeseTests.getTestSign(test['TESTCLASS'], testKey)} 
from file {Logger.WARNING}{Logger.UNDERLINE}{testFile}{Logger.ENDC}{Logger.BOLD}
================================="""
            if ("IGNORE" in test.keys()):
                testHeader += f"\n{Logger.WARNING}IGNORING\n========"
                Logger.bold(testHeader, False)
                CheeseTests.testIgnoredCount += len(test["METHODS"].keys())
                CheeseTests.testTotalCount += len(test["METHODS"].keys())
                continue
            Logger.bold(testHeader, False)

            for methodKey in test["METHODS"].keys():
                CheeseTests.testTotalCount += 1
                
                method = test["METHODS"][methodKey]
                CheeseTests.oneTest(method, methodKey)

        
        if (CheeseTests.testFailCount + CheeseTests.testErrorCount != 0):
            result = Logger.FAIL
        else:
            result = Logger.OKGREEN

        Logger.bold(f"""
{20*'='}{result}Testing done{Logger.ENDC}{Logger.BOLD}{20*'='}
total: {CheeseTests.testTotalCount}
{Logger.OKGREEN}success{Logger.ENDC}{Logger.BOLD}: {CheeseTests.testOkCount}
{Logger.FAIL}fail{Logger.ENDC}{Logger.BOLD}: {CheeseTests.testFailCount}
{Logger.FAIL}error{Logger.ENDC}{Logger.BOLD}: {CheeseTests.testErrorCount}
{Logger.WARNING}ignored{Logger.ENDC}{Logger.BOLD}: {CheeseTests.testIgnoredCount}
        """, False)

        if (result == Logger.FAIL):
            sys.exit(1)
        CheeseRepository.stopTesting()

    @staticmethod
    def oneTest(method, methodKey):
        tm = time.time()
        testMessage = f"{CheeseTests.getTestSign(method['TEST'], methodKey)} -> "

        try:
            if ("IGNORE" not in method.keys()):
                method["OBJECT"]()
                testMessage += f"[{Logger.OKGREEN}OK{Logger.ENDC}{Logger.BOLD}]     $TIME$"
                CheeseTests.testOkCount += 1
            else:
                testMessage += f"[{Logger.WARNING}IGNORED{Logger.ENDC}{Logger.BOLD}]"
                CheeseTests.testIgnoredCount += 1
        except TestError as e:
            # FAIL
            testMessage += f"""[{Logger.FAIL}FAIL{Logger.ENDC}{Logger.BOLD}]    $TIME$
{Logger.WARNING}"{str(e.comment)}"{Logger.ENDC}{Logger.BOLD}
Value should be: {Logger.OKGREEN}{str(e.template)}{Logger.ENDC}{Logger.BOLD}
But it was: {Logger.FAIL}{str(e.value)}{Logger.ENDC}{Logger.BOLD}
"""
            CheeseTests.testFailCount += 1
        except Exception as e:
            # ERROR
            Logger.bold(testMessage + f"[{Logger.FAIL}ERROR{Logger.ENDC}{Logger.BOLD}]", False)
            Error.handleError(None, e)
            CheeseTests.testErrorCount += 1
            return

        tm = time.time() - tm
        Logger.bold(testMessage.replace("$TIME$", CheeseTests.formatTime(tm)), False)
        
    @staticmethod
    def getTestSign(name, pthName):
        return f"{Logger.OKCYAN}{name}{Logger.ENDC} - {Logger.OKBLUE}{pthName}{Logger.ENDC}{Logger.BOLD}"

    @staticmethod
    def formatTime(tm):
        ms = tm * 1000
        ns = tm * 1000000
        m = tm / 60
        h = m / 60

        if (h >= 1):
            return (f"{int(h)} hours " + 
            f"{int(m - int(h)*60)} minutes")
        if (m >= 1):
            return (f"{int(h)} hours " + 
            f"{int(m - int(h)*60)} minutes " + 
            f"{int(tm - int(m)*60)} seconds")
        if (tm >= 1):
            return str((int(tm*1000)/1000)) + " s"
        if (ms >= 1):
            return str((int(ms*1000)/1000)) + " ms"
        if (ns >= 1):
            return str((int(ns*1000)/1000)) + " ns"
        return "0 s"

# running test for one file
"""
curframe = inspect.currentframe()
calframe = inspect.getouterframes(curframe)[6]
fileName = ResMan.getFileName(calframe.filename)
if (fileName != "cheese.py"):
    Settings.allowDebug = True
    ResMan.setPath(calframe.filename.replace(fileName, ""))
    CheeseTests.testFiles([calframe.filename])"""