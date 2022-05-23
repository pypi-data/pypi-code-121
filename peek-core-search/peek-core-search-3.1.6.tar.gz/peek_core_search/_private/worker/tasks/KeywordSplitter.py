import string
from typing import Set


def _splitFullTokens(keywordStr: str) -> Set[str]:
    if not keywordStr:
        return []

    # Lowercase the string
    keywordStr = keywordStr.lower()

    # Remove punctuation
    tokens = "".join([c for c in keywordStr if c not in string.punctuation])

    # Strip and Split words, filter out words less than three letters
    return set([w.strip() for w in tokens.split(" ") if 2 <= len(w)])


def splitFullKeywords(keywordStr: str) -> Set[str]:
    """Split Full Keywords

    This tokenizer function is used for search strings loaded into
    the fullKwPropertiesJson field of the SearchObject.

    This exists, because not all data is suitable for partial keywork search
    for example IDs like J00001223COMP

    """
    tokens = _splitFullTokens(keywordStr)
    tokens = ["^%s$" % t for t in tokens if 2 <= len(t)]

    return set(tokens)


def splitPartialKeywords(keywordStr: str) -> Set[str]:
    """Split Partial Keywords

    This tokenizer function is used for search strings loaded into the
    partialKwPropertiesJson field of the SearchObject.

    This will tokenize
    * all the smaller keywords as a full keyword,
    * all numbers as full keywords
    * all remaining items will be tokenized in a rolling three char method.

    :param keywordStr: The string to tokenize

    """
    # Strip and Split words, filter out words less than three letters
    tokens = _splitFullTokens(keywordStr)

    # Split the words up into tokens, this creates partial keyword search support
    tempTokens, tokens = tokens, []
    for token in tempTokens:
        # Partial tokenize the other words.
        for index in range(max(1, len(token) - 2)):
            tokens.append(("" if index else "^") + token[index : index + 3])

    return set(tokens)


def twoCharTokens(tokens: Set[str]) -> Set[str]:
    def isTwoChar(token: str) -> bool:
        if token.endswith("$") and len(token) == 4:
            return True
        if token.startswith("^") and len(token) == 3:
            return True
        return False

    return set([t for t in tokens if isTwoChar(t)])
