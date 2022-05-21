#cheese

import os

from Cheese.resourceManager import ResMan
from Cheese.finder import Finder

class TestsBuilder:
    
    @staticmethod
    def build(parent):
        tests = []

        for root, dirs, files in os.walk(ResMan.root()):
            for file in files:
                if (not file.endswith(".py")): continue

                path = os.path.join(root, file)

                if (Finder.isSomething(path, "testclass")): 
                    tests.append(path)

        parent.doJson(tests, "TESTS", ["TESTCLASS"], [("TEST", [])])

