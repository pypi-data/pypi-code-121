from pathlib import Path
from pkg_resources import resource_filename


def get_data(folder: str, filename: str) -> list[str]:
    '''
    Returns list of strings gathered from a certain datafile in a certain folder

    Args:
        folder (str): The name of a folder
        filename (str): The name of a datafile

    Returns:
        list[str]: The gathered list of strings
    '''
    words = []
    data_path = Path(resource_filename('randword', 'data'))
    filepath = data_path / folder / f'{filename}.txt'

    with open(filepath, 'r') as pos_file:
        pos_words = pos_file.readlines()
        words.extend(pos_words)

    return [word.rstrip() for word in words]
