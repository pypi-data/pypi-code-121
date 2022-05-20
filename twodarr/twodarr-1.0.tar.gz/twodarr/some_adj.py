from twodarr.check_bound import check_bound

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
            adj.append({'x':spot['x'], 'y':spot['y'], 'val':arr[spot['y']][spot['x']]})
        elif (default != '\0'):
            adj.append({'x':spot['x'], 'y':spot['y'], 'val':default})
    return adj