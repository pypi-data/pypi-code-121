import re
import os
from pathlib import Path, PureWindowsPath, PurePosixPath


class PathPattern:
    def __init__(self, pattern: str):
        self.pattern = pattern #unadulterated pattern, as passed.        
        self.normalizedPathPattern = PurePosixPath(self.pattern)

        try:
            re.compile( str(self.normalizedPathPattern) ) # will raise exception if needed
        except :
            raise ValueError(r"""Invalid regex: a common error is to use Windows path (with backslahes \\).
                Normalize your path with "/" instead of "\" as a separator. 
                Windows path cannot be used directly: it is not possible to decide
                the meaning of escaped characters:  C:\newbie\dccote\test.tiff  Is it a newline character? 
                The solution could be to have the user escape everything but then the newline must be "unescaped"
                for the regex.""")

    @property
    def directory(self):
        dirName = os.path.dirname(self.normalizedPathPattern)
        if dirName == '':
            dirName = '.'
        return dirName  # DOES NOT convert to native Windows or Unix

    @property
    def nativeDirectory(self):
        return str(Path(self.directory))

    @property
    def basePattern(self):
        return os.path.basename(self.pattern)

    @property
    def nativeBasePattern(self):
        return str(Path(self.basePattern))

    @property
    def extension(self):
        dummy, extensionWithPeriod = os.path.splitext(self.pattern)
        return extensionWithPeriod[1:]

    @property
    def hasCaptureGroups(self) -> bool:
        if re.search(r"\(.+\)", self.pattern):
            return True
        else:
            return False

    @property
    def numberOfCaptureGroups(self) -> int:
        captureGroups = re.findall(r"(\(.+?\))", self.pattern)
        return len(captureGroups)

    @property
    def isPythonFormatString(self) -> bool:
        if re.search(r"\{\d+.*?\}", self.pattern):
            return True
        else:
            return False

    @property
    def numberOfFormatGroups(self) -> int:
        formatGroups = re.findall(r"\{\d+.*?\}", self.pattern)
        return len(formatGroups)

    @property
    def isWritePattern(self) -> bool:
        if self.isPythonFormatString:
            return True
        else:
            return False

    @property
    def isReadPattern(self) -> bool:
        if self.hasCaptureGroups:
            return True
        else:
            return False

    def matchingFiles(self) -> list:
        if self.isWritePattern:
            raise ValueError("Patterns with format strings are for writing files, not reading")

        paths = []
        for filename in os.listdir(self.directory):
            if re.match(self.basePattern, filename):
                filePath = os.path.join(self.directory, filename)
                paths.append(filePath)
        paths.sort()
        return paths

    def filePathWithIndex(self, i: int, j: int = None, k: int = None):
        if self.isReadPattern:
            raise ValueError("Patterns with capture groups are for reading files, not writing")

        passedArguments = 1
        if i is not None and j is not None and k is None:
            passedArguments = 2
        elif i is not None and j is not None and k is not None:
            passedArguments = 3

        if self.numberOfFormatGroups != passedArguments:
            raise ValueError(
                "Pattern has {0} indices, only passed {1}".format(self.numberOfFormatGroups, passedArguments))

        if self.numberOfFormatGroups == 1:
            filePath = self.pattern.format(i)
        elif self.numberOfFormatGroups == 2:
            filePath = self.pattern.format(i, j)
        elif self.numberOfFormatGroups == 3:
            filePath = self.pattern.format(i, j, k)

        return filePath
