#cheese

from Cheese.Logger import Logger

class Finder:

    @staticmethod
    def isSomething(file, type):
        if (not file.endswith(".py")): return False
        with open(file, "r") as f:
            data = f.read()
        
        if (data.find("#@" + type) != -1):
            return True
        return False

    classAnnotations = [
        "#@controller",
        "#@repository",
        "#@dbscheme",
        "#@dbmodel",
        "#@model",
        "#@testclass",
        "#@ignore"
    ]
    methodAnnotations = [
        "#@post",
        "#@get",
        "#@query",
        "#@commit",
        "#@return",
        "#@test",
        "#@ignore"
    ]

    def loadFile(self, file):
        self.file = file
        with open(file, "r") as f:
            dLines= f.readlines()

        self.dataLines = []
        for line in dLines:
            self.dataLines.append(line.strip())

    def findClasses(self):
        return self.findAnnotatedStructure(self.classAnnotations, "class")

    def findMethods(self):
        return self.findAnnotatedStructure(self.methodAnnotations, "def")

    # finds all annotated structures like class and def
    def findAnnotatedStructure(self, annotationSet, name):
        structures = []

        for i, line in enumerate(self.dataLines):
            
            if (line.startswith(name)):
                annots = self.isAnnotated(i, annotationSet)
                if (not annots): continue

                structureName = "".join(line.split(" ")[1:]).split("(")[0]
                structures.append(
                    {
                        "NAME": structureName,
                        "ANNOTATIONS": annots,
                        "INDEX": i
                    }
                )
        return structures

    # runs through lines above line while they are annotations or it is end of file
    def isAnnotated(self, index, annotationSet):
        endIndex = index
        index -= 1
        
        while (index > 0): # finds start of annotating and commenting
            upperLine = self.dataLines[index]

            if (upperLine.startswith("@") or 
                upperLine.startswith("#")):
                index -= 1
            else:
                break

        newAnn = ""
        annots = []

        for i in range(index, endIndex):
            line = self.dataLines[i]

            if (line.startswith("@")): continue # python annotation skipping this line

            if (not self.startsWith(line, annotationSet)): continue
            
            newAnn = line
            indexL = i
            while (not newAnn.endswith(";")):
                indexL += 1
                if (indexL < len(self.dataLines)):
                    line = self.dataLines[indexL]

                    if (self.startsWith(line, annotationSet) or 
                        self.startsWith(line, "def")):
                        self.raiseError(indexL+1, f"Missing end of annotation {self.wOkG(self.getAnnotationType(newAnn))}")
                else:
                    self.raiseError(indexL+1, f"Missing end of annotation {self.wOkG(self.getAnnotationType(newAnn))}")
                newAnn += self.getMultiline(indexL+1, line)

            annots.append(newAnn)

        if (len(annots) == 0): return False

        retAnns = {}
        for ann in annots:
            retAnns[self.getAnnotationType(ann, True)] = self.getAnnotationContent(ann)

        return retAnns

    def hasAnnotation(self, structure, annotation):
        return annotation in structure["ANNOTATIONS"]

    # helpful methods

    def startsWith(self, string, starterSet):
        for starter in starterSet:
            if (string.startswith(starter)):
                return True
        return False

    def getAnnotationType(self, annotation, notSing=False):
        if (notSing):
            annot = annotation.split(" ")[0].replace("#@", "")
        else:
            annot = annotation.split(" ")[0]

        if (annot.endswith(";")): annot = annot[:-1]
        return annot

    def getMultiline(self, index, line):
        if (line.startswith("#")):
            return " " + line[1:].strip()
        self.raiseError(index, "Multiline annotation have to start with '#'")

    def getAnnotationContent(self, annotation):
        annType = self.getAnnotationType(annotation)
        annTypeS = self.getAnnotationType(annotation, True)

        content = self.rreplace(annotation.replace(annType, "", 1), ";")
        if (annTypeS == "query" or annTypeS == "commit"):
            content = content.replace("\"", "", 1)
            content = self.rreplace(content, "\"")

        return content.strip()

    def rreplace(self, string, oldString, newString="", maxReplace=1):
        return newString.join(string.rsplit(oldString, maxReplace))
                
    # ERRORS

    def raiseError(self, index, comment):
        raise SyntaxError(f"{comment} in {self.wWar(self.file)} at line {self.wOkG(index)}")

    def raiseDictError(self, name, file):
        raise SyntaxError(f"Missing '{self.wOkG(name)}' name in {self.wWar(file)}")

    def validateKey(self, key, dict, file):
        if (key not in dict.keys()):
            self.raiseDictError(key, file)

    def wWar(self, string):
        return f"{Logger.WARNING}{string}{Logger.FAIL}"

    def wOkG(self, string):
        return f"{Logger.OKGREEN}{string}{Logger.FAIL}"
    
