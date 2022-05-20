def check_bound(arr:list, y:int, x:int):
    '''given a 2D array, and coords to a spot, returns whether the coords are valid\n
    this is assuming you don't want to wrap around when values get negative'''
    if (y >= 0 and x >= 0 and y < len(arr) and x < len(arr[0])):
        return True
    return False

def all_adj(arr:list, y:int, x:int, default = '\0'):
    '''returns all 8 surrounding squares as dicts of {x,y,val}\n
    if a default is given, it will be put in for val when out of bounds, otherwise out of bounds will be left out'''
    adj = []
    for row in range(-1,2):
        for column in range(-1,2):
            if (check_bound(arr, y+row, x+column) and [row,column] != [0,0]):
                adj.append({'x':x+column, 'y':y+row, 'val':arr[y+row][x+column]})
            elif ([row,column] != [0,0] and default != '\0'):
                adj.append({'x':x+column, 'y':y+row, 'val':default})
    return adj

def some_adj(arr:list, y:int, x:int, default = '\0'):
    '''returns the 4 immediate squares as dicts of {x,y,val}\n
    if a default is given, it will be put in for val when out of bounds, otherwise out of bounds will be left out'''
    adj = []
    coords = [{'x':x,'y':y-1},
            {'x':x-1, 'y':y},
            {'x':x+1, 'y':y},
            {'x':x, 'y':y+1},]
    for spot in coords:
        if (check_bound(arr, spot['y'], spot['x'])):
            adj.append({'x':spot['x'], 'y':y+spot['y'], 'val':arr[spot['y']][spot['x']]})
        elif (default != '\0'):
            adj.append({'x':spot['x'], 'y':spot['y'], 'val':default})
    return adj