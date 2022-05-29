from string import punctuation


def remove_punctuation(text: str) -> str:
    """Remove punctuation from a string.

    Parameters
    ----------
    text : str
        Text to be processed.

    Returns
    -------
    str
        Text with punctuation removed.

    Examples
    --------
    >>> remove_punctuation("I think, therefore I am. --Descartes")
    'I think therefore I am Descartes'
    """
    return text.translate(str.maketrans("", "", punctuation))
