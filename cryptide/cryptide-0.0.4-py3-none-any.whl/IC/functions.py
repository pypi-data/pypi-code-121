from collections import Counter

from unidecode import unidecode

from cryptide.IC.reference_data import IC_eq


def checker_ic(ic: float, stopper: float = 0.04) -> bool:
    """
    Check if the index of coincidence from inout are higher than stopper
    Args:
        ic (float): The index of coincidence to check
        stopper (float, optional): The stopper value

    Returns:
        bool: Return True if the ic input are higher than stopper
    """
    if ic > stopper:
        return True


def list_aggregation(iterable: iter, length: int = 2) -> list:
    """
    Gonna group length by length the iterable input
    Args:
        iterable (iter): The input to group
        length (int, optional): The number of aggregation

    Exemples:
        This is an example

            list_aggregation([1, 2, 3, 4, 5, 6], 2)
            # [(1, 2), (3, 4), (5, 6)]

            list_aggregation([1, 2, 3, 4, 5, 6], 3)
            # [(1, 2, 3), (4, 5, 6)]

    Returns:
        List(tuple) : the data aggregated
    """
    return list(zip(*([iter(iterable)] * length)))


def checker_and_compute_ic(chain: iter, stopper: float = 0.04, multiplier: int = 1, beautifier: bool = False) -> bool:
    """
    The function gonna comput the index of coincidence of input and return True if the ic is higher than stopper
    Args:
        chain (iter): The data to compute the index of coincidence
        stopper (float, optional): The stopper value to return True
        multiplier (int, optional): Gonna increase your data *multiplier* x chain
        beautifier (bool, optional): If True the input dana gonna be Asciier before computing index of coincidence

    Returns:
        bool: Return True if the ic input are higher than stopper
    """
    ic = compute_ic(chain, multiplier=multiplier, beautifier=beautifier)
    return checker_ic(ic, stopper)


def what_ic(ic: float) -> str:
    """
    Will find the nearest language index of coincidence of the input
    Args:
        ic (float): The index of coincidence to find

    Returns:
        str: The nearest language of inpout
    """
    closer = min(IC_eq, key=lambda x: abs(x - ic))
    return IC_eq[closer]


def compute_ic(chain: iter, multiplier: int = 1, beautifier: bool = False) -> float:
    """
    Comput the Index of coincidence
    Args:
        chain (iter): The string to comput
        multiplier (int, optional): Gonna increase your data *multiplier* x chain
        beautifier (bool, optional): If True the input dana gonna be Asciier before computing index of coincidence

    Returns:
        float: The Index of coincidence from input data
    """
    if beautifier:
        chain = unidecode(chain).lower()
    chain *= multiplier
    counter = Counter(chain)
    sums = sum(map(lambda x: x * (x - 1), counter.values()))
    lenner = len(chain)
    dominator = lenner * (lenner - 1)
    return sums / dominator


if __name__ == '__main__':
    import timeit

    text = """Demain, dès l'aube, à l'heure où blanchit la campagne,
    Je partirai. Vois-tu, je sais que tu m'attends.
    J'irai par la forêt, j'irai par la montagne.
    Je ne puis demeurer loin de toi plus longtemps.
    Je marcherai les yeux fixés sur mes pensées,
    Sans rien voir au dehors, sans entendre aucun bruit,
    Seul, inconnu, le dos courbé, les mains croisées,
    Triste, et le jour pour moi sera comme la nuit.
    Je ne regarderai ni l'or du soir qui tombe,
    Ni les voiles au loin descendant vers Harfleur,
    Et quand j'arriverai, je mettrai sur ta tombe
    Un bouquet de houx vert et de bruyère en fleur.
    Victor Hugo - Les Contemplations"""
    btext = text.encode()

    nb = 100

    x = compute_ic(btext)
    print(x)
    setup = "from __main__ import (compute_ic, btext, text)"
    x = timeit.timeit("compute_ic(btext)", setup=setup, number=nb)
    print(x)
