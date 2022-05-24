from ._CSVFile import CSVFile


def save(csv: CSVFile, filename: str, encoding: str = 'utf-8'):
    """
    Saves the given CSV file to disk.

    :param csv:        The CSV file to save.
    :param filename:    The filename to save the file under.
    :param encoding:    The string encoding to use.
    """
    with open(filename, 'w', encoding=encoding) as file:
        file.write(str(csv))
