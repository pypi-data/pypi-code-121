def bytes_representation(bytes_chain: bytes) -> list:
    """
    Give a representation of bytes of bits
    Args:
        bytes_chain (byte): Input to represent

    Returns:
        List(str): The bytes representation of input
    """
    return [f"{byte:08b}" for byte in bytes_chain]


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

    x = bytes_representation(btext)
    print(x)
    setup = "from __main__ import (bytes_representation, btext, text)"
    x = timeit.timeit("bytes_representation(btext)", setup=setup, number=nb)
    print(x)
