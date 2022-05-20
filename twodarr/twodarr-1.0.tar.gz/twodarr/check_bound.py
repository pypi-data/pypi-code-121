def check_bound(arr:list, y:int, x:int):
    '''given a 2D array, and coords to a spot, returns whether the coords are valid\n
    this is assuming you don't want to wrap around when values get negative'''
    if (y >= 0 and x >= 0 and y < len(arr) and x < len(arr[0])):
        return True
    return False