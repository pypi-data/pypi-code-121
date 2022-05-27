import os
import re


def findFiles(directory: str, extension: str) -> list:
    # Although os.walk is slow, I haven't found a faster way to find files in a directory and sub directories.
    # In python 3.x, os.walk was modified to use os.scandir, which greatly improved its performances. I doubt
    # there is a faster way to do this.
    filesFound = []
    for root, directories, files in os.walk(os.path.normpath(directory)):
        for file in files:
            if re.search(r'^.*\.{}$'.format(extension), file, re.IGNORECASE):
                filesFound.append(os.path.join(root, file))
    return filesFound


def findFolderInPath(folder: str, path: str):
    basename = os.path.basename(path)
    if basename == '':
        return False
    elif basename == folder:
        return folder
    else:
        return findFolderInPath(folder, os.path.dirname(path))


def sqliteDataTypes() -> list:
    # This is a list of data types and affinities for sqlite entries. Used to check if a type is valid.
    # Affinities with a range of values would work even if the given range is wrong. They are more like guidelines and
    # less like rules. Nonetheless, for the sake of cleanliness, these guidelines are currently enforced.
    return ['INT', 'INTEGER', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT', 'UNSIGNED BIG INT', 'INT2', 'INT8',
            r'CHARACTER\(([1-9]|1\d|20)\)|CHARACTER$',
            r'VARCHAR\(([1-9]|\d{2}|1\d{2}|2[0-4]\d|2[0-5][0-5])\)|VARCHAR$',
            r'VARYING CHARACTER\(([1-9]|\d{2}|1\d{2}|2[0-4]\d|2[0-5][0-5])\)|VARYING CHARACTER$',
            r'NCHAR\(([1-9]|[1-4]\d|5[0-5])\)|NCHAR$', r'NATIVE CHARACTER\(([1-9]|[1-6]\d|70)\)|NATIVE CHARACTER$',
            r'NVARCHAR\(([1-9]|\d{2}|100)\)|NVARCHAR$', 'TEXT', 'CLOB', 'BLOB', 'REAL', 'DOUBLE', 'DOUBLE PRECISION',
            'FLOAT', 'NUMERIC', r'DECIMAL\(([1-9]|10),([0-5])\)|DECIMAL$', 'BOOLEAN', 'DATE', 'DATETIME']


def checkIfValidDataType(dataType: str) -> bool:
    try:
        for dType in sqliteDataTypes():
            if re.search(dType, dataType, re.IGNORECASE):
                return True
        return False
    except:
        return False


if __name__ == '__main__':
    print(findFolderInPath('Usersi', __file__))
    pass