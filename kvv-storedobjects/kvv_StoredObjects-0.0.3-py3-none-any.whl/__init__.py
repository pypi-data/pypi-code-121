from author import Author
from department import Department
from publication import Publication
from university import University

_univer = None


def getUniversity():
    global _univer
    if _univer is None:
        _univer = University()
    return _univer


if __name__ == "__main__":
    getUniversity()