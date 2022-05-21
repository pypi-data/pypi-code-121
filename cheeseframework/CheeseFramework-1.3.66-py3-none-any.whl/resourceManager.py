#cheese

import os
import math

class ResMan:

    @staticmethod
    def setPath(path):
        ResMan.path = str(path)

    # return name of file from path
    @staticmethod
    def getFileName(path):
        return os.path.basename(path)

    # return relative path from
    @staticmethod
    def getRelativePathFrom(path, fromPath):
        return path.replace(fromPath, "")

    # remove / from start or end
    @staticmethod
    def removeSlash(path, start=True):
        if (path[0] == "/" and start):
            path = path[1:]
        elif (path[-1] == "/" and not start):
            path = path[:-1]
        return path

    # joins two path together
    @staticmethod
    def joinPath(*args):
        if (len(args) < 1): return ""
        if (len(args) == 1): return args[0]

        paths = []
        paths.append(ResMan.removeSlash(args[0], False))

        for path in args[1:-1]:
            p = ResMan.removeSlash(path)
            p = ResMan.removeSlash(p, False)
            paths.append(p)

        paths.append(ResMan.removeSlash(args[-1]))
        return os.path.join(*paths)

    # root dir of project
    @staticmethod
    def root(*paths):
        return ResMan.joinPath(ResMan.path, *paths)

    # all source codes of project
    @staticmethod
    def src(*paths):
        return ResMan.root("src", *paths) 

    # other resources of project
    @staticmethod
    def resources(*paths):
        return ResMan.root("resources", *paths)

    # logs
    @staticmethod
    def logs(*paths):
        return ResMan.root("logs", *paths)

    # tests
    @staticmethod
    def tests(*paths):
        return ResMan.src("tests", *paths)

    # dir from which CheeseFramework is able to serve files (index.html) 
    @staticmethod
    def web(*paths):
        return ResMan.root("web", *paths)

    # dir for error sites
    @staticmethod
    def error(*paths):
        return ResMan.web("errors", *paths)

    # admin
    @staticmethod
    def admin(*paths):
        return ResMan.root(".admin", *paths)

    # metadata
    @staticmethod
    def metadata():
        return ResMan.root(".metadata")

    # convert bytes
    @staticmethod
    def convertBytes(bytes):
        if bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(bytes, 1024)))
        p = math.pow(1024, i)
        s = round(bytes / p, 2)
        return "%s %s" % (s, size_name[i])