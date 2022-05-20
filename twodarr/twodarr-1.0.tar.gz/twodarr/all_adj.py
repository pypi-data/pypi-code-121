from twodarr.check_bound import check_bound

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