#cheese

import os
import json

from Cheese.resourceManager import ResMan
from Cheese.Logger import Logger
from Cheese.metadata import Metadata
from Cheese.controllerBuilder import ControllerBuilder
from Cheese.repositoriesBuilder import RepositoriesBuilder
from Cheese.testsBuilder import TestsBuilder
from Cheese.securityBuilder import SecurityBuilder
from Cheese.finder import Finder
from Cheese.cheeseController import CheeseController as cc

"""
Builds Cheese Application
"""

class ProjectBuilder:

    dontNeedInit = ["REPOSITORIES"]

    def __init__(self):
        self.dictJson = {}

    def build(self):
        try:
            self.dictJson = {
                "CONTROLLERS": {}, 
                "REPOSITORIES": {}, 
                "TESTS": {},
                "ADMIN": {},
                "SECURITY": {},
                "SECRETS": {}
            }

            if (not os.path.exists(ResMan.root("adminSettings.json"))):
                Logger.bold("SKIPPING BUILD")
                return True

            #build controllers
            ControllerBuilder.build(self)

            #build repositories
            RepositoriesBuilder.build(self)

            #build tests
            TestsBuilder.build(self)

            #build security rules
            SecurityBuilder.build(self)

            Metadata.save(self.dictJson)

            self.count()
            return True
        except SyntaxError as e:
            Logger.bold(f"{Logger.FAIL}{e}", False, False)
            return False
        except Exception as e:
            raise
            
    def count(self):
        data = Metadata.read()

        gets = 0
        posts = 0
        queries = 0
        commits = 0
        for key in data.keys():
            if (key == "SECRETS" or
                key == "ADMIN" or 
                key == "SECURITY"): continue
                
            for pKey in data[key].keys():
                cont = data[key][pKey]
                for methodKey in cont["METHODS"].keys():
                    method = cont["METHODS"][methodKey]

                    if ("GET" in method): gets += 1
                    elif ("POST" in method): posts += 1
                    elif ("QUERY" in method): queries += 1
                    elif ("COMMIT" in method): commits += 1

        Logger.info(
            f"""
{Logger.OKGREEN}====Build successful====
    {Logger.OKCYAN}Controllers: {len(data["CONTROLLERS"].keys())}
        {Logger.OKBLUE}GET methods: {gets}
        {Logger.OKBLUE}POST methods: {posts}

    {Logger.OKCYAN}Repositories: {len(data["REPOSITORIES"].keys())}
        {Logger.OKBLUE}query methods: {queries}
        {Logger.OKBLUE}commit methods: {commits}{Logger.ENDC}
            """,
        False, False)

    def doJson(self, srcCodes, dictName, mainAnnotations, methodAnnotations):
        self.finder = Finder()
        for code in srcCodes:
            self.finder.loadFile(code)
            
            classes = self.finder.findClasses()
            methods = self.finder.findMethods()

            lastClassIndex = len(self.finder.dataLines)
            if (len(classes) > 1):
                lastClassIndex = classes[1]
            for cls in classes:
                annotations = cls["ANNOTATIONS"]

                validation = self.validateJson(annotations, *mainAnnotations)
                if (validation != True):
                    self.finder.raiseError(cls["INDEX"], f"There is missing {self.finder.wOkG(validation)} annotations")

                file = ResMan.getRelativePathFrom(code, ResMan.root()).replace(".py", "")
                file = file.replace("\\", "/")
                if (file.startswith("/")):
                    file = file[1:]

                methodsJson, lastClassIndex = self.doMethods(cls, methods, lastClassIndex, *methodAnnotations)

                clsName = cls["NAME"]
                if (clsName.endswith(":")):
                    clsName = clsName[:-1]

                self.dictJson[dictName][clsName] = {
                    "FILE": file,
                    "METHODS": methodsJson
                }

                for ann in mainAnnotations:
                    self.dictJson[dictName][clsName][ann] = annotations[ann.lower()]

                for ann in annotations.keys():
                    if (ann.upper() not in mainAnnotations):
                        self.dictJson[dictName][clsName][ann.upper()] = annotations[ann]

    def doMethods(self, cls, methods, lastClassIndex, *methodAnnotations):
        methodsJson = {}

        newLastClassIndex = int(cls["INDEX"])
        for method in methods:

            if (int(method["INDEX"]) > int(cls["INDEX"]) and int(method["INDEX"]) < int(lastClassIndex)):
                newLastClassIndex = method["INDEX"]
                methodsJson[method["NAME"]] = {} 

                annots = method["ANNOTATIONS"]
                mainAnnots = []
                for ann in methodAnnotations: # creates array of possible annotations
                    mainAnnots.append(ann[0])

                usedAnnotation = self.validateJsonOne(annots, *mainAnnots) # finds if there is any of main annotations
                usedAnnotMethod = ()
                for a in methodAnnotations: #  find used annotation
                    if (a[0] == usedAnnotation):
                        usedAnnotMethod = a
                        break
                for par in usedAnnotMethod[1]: 

                    if (par[0].lower() not in annots):
                        
                        if (len(par) == 2):
                            methodsJson[method["NAME"]][par[0]] = par[1]
                        else:
                            self.finder.raiseError(method["INDEX"], 
                            f"Annotation {self.finder.wOkG('#@' + usedAnnotation)}" +
                            f" needs annotation {self.finder.wOkG('#@' + par[0].lower())}")
                    else:
                        methodsJson[method["NAME"]][par[0]] = annots[par[0].lower()]

                for ann in annots:
                    if (ann not in methodsJson):
                        methodsJson[method["NAME"]][ann.upper()] = annots[ann]

        return methodsJson, newLastClassIndex

    # helpfull methods

    def validateJson(self, dict, *args):
        for a in args:
            if (not cc.validateJson([a.lower()], dict)):
                return a
        return True

    def validateJsonOne(self, dict, *args):
        for a in args:
            if (cc.validateJson([a.lower()], dict)):
                return a
        return False


