import university

_univer = None


def getUniversity():
    global _univer
    if _univer is None:
        _univer = university.University()
    return _univer


if __name__ == "__main__":
    getUniversity()