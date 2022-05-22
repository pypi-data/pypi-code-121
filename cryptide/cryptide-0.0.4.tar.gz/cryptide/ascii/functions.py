def get_unascii_stat(bytes_chain: bytes) -> float:
    """
    This test gonna check the percent of non-ascii data
    Args:
        bytes_chain (bytes): The bytes to check

    Returns:
        float: The percent of non-ascii data
    """
    header = [1 for byte in bytes_chain if byte > 127]
    return len(header) / len(bytes_chain)


def unascii_stoper(bytes_chain: bytes, ratio: float = 0.25) -> bool:
    """
    This test gonna check the percent of non-ascii data, through the most significant bit
    Args:
        bytes_chain (bytes): The bytes to check
        ratio (float, optinal): Return True if the most significant bit ratio is under ration

    Returns:
        bool: Return True if the percent of non-ascii data from input is less than ratio
    """
    if get_unascii_stat(bytes_chain) <= ratio:
        return True


def get_ascii_readable_stat(bytes_chain: bytes) -> float:
    """
    This test gonna compute the percent of readable caractere from Humain
    Args:
        bytes_chain (bytes): The bytes to check

    Returns:
        float: The percent of ascii values between 32 and 127
    """
    header = [1 for byte in bytes_chain if byte > 31 and byte < 127]
    return len(header) / len(bytes_chain)


def ascii_readable_stoper(bytes_chain: bytes, ratio: float = 0.75) -> bool:
    """
    This test gonna check if the bytes input are readable by Humain
    Args:
        bytes_chain (bytes): The bytes to check
        ratio (float, optional): Return True if the most significant bit ratio is under ration

    Returns:
        bool: Return True if the percent of ascii data from input is higher than ratio
    """
    if get_ascii_readable_stat(bytes_chain) >= ratio:
        return True


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

    x = get_ascii_readable_stat(btext)
    print(x)
    setup = "from __main__ import (get_ascii_readable_stat, btext, text)"
    x = timeit.timeit("get_ascii_readable_stat(btext)", setup=setup, number=nb)
    print(x)
