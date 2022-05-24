
def iterlen(iterator):
    '''returns length of iterator'''
    return sum(1 for _ in iterator)

def get_extent(iterator):
    '''returns (min, max) of iterator'''
    iterator = iter(iterator)
    m = M = next(iterator)
    for elem in iterator:
        if elem < m: m = elem
        elif elem > M: M = elem
    return (m,M)
