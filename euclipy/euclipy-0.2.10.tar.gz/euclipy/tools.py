def pairs_in_iterable(iterable):
    return [(a, b) for idx, a in enumerate(iterable) for b in iterable[idx + 1:]]