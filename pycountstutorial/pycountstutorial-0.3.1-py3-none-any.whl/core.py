from collections import Counter
from pathlib import Path
from string import punctuation


def load_text(input_file):
    """Load text from a text file and return as a string.

    Parameters
    ----------
    input_file : str, pathlib.Path
        Path to text file.

    Returns
    -------
    str
        Text file contents.

    Examples
    --------
    >>> load_text("text.txt")
    """
    path = input_file if isinstance(input_file, Path) else Path(input_file)
    return path.resolve().read_text()


def clean_text(text):
    """Lowercase and remove punctuation from a string.

    Parameters
    ----------
    text : str
        Text to clean.

    Returns
    -------
    str
        Cleaned text.

    Examples
    --------
    >>> clean_text("Early optimization is the root of all evil!")
    'early optimization is the root of all evil'
    """
    text = text.lower()
    for p in punctuation:
        text = text.replace(p, "")
    return text


def count_words(input_file):
    """Count words in a text file.

    Words are made lowercase and punctuation is removed before counting.

    Parameters
    ----------
    input_file : str, pathlib.Path
        Path to text file.

    Returns
    -------
    collections.Counter
        dict-like object where keys are words and values are counts.

    Examples
    --------
    >>> count_words("text.txt")
    """
    text = load_text(input_file)
    text = clean_text(text)
    words = text.split()
    return Counter(words)
