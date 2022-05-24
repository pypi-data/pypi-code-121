import re


def start_sentence_with_capital(s: str) -> str:
    """
    Strip unecessary white space.
    Also start every sentence with a capital.
    Sentence should be ended by a point.
    Args:
        s (str): the input text.

    Returns:
        str: The output texte
    """
    sentence = []

    for x in s.split("."):
        x = x.strip()
        if len(x) > 2:
            y = x[0].upper() + x[1:]
            sentence.append(re.sub(" +", " ", y))
        else:
            sentence.append(re.sub(" +", " ", x))
    final = ". ".join(sentence)
    # On postraite pour les ...
    sentence = []
    for x in final.split("."):
        sentence.append(x.rstrip())

    return ".".join(sentence)


def modify_unit(s: str) -> str:
    return s.replace(" celsius", "°C")


if __name__ == "__main__":
    s = (
        "je suis un petit test.Et je suis pas trop content.     "
        "par contre c'etr Trop     classe lea Completion..."
    )
    print(start_sentence_with_capital(s))
