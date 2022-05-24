from ._ARFFFile import ARFFFile


def save(arff: ARFFFile, filename: str, encoding: str = 'utf-8'):
    """
    Saves the given ARFF file to disk.

    :param arff:        The ARFF file to save.
    :param filename:    The filename to save the file under.
    :param encoding:    The string encoding to use.
    """
    with open(filename, 'w', encoding=encoding) as file:
        file.write(str(arff))
