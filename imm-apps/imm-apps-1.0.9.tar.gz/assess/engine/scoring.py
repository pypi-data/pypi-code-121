
skill_levels = {
    '0': 'A',  # if the second number is 0 or 1, the level is A
    '1': 'A',
    '2': 'B',
    '3': 'B',
    '4': 'C',
    '5': 'C',
    '6': 'D',
    '7': 'D'
}

def getNOCLevel(noc):
    level = ''
    if noc[0] == '0':
        if noc[1] == '0':
            level = '00'
        else:
            level = '0'
    else:
        level = skill_levels.get(noc[1],None)
    return level

# key is factor, value is points. Most common scoring way
def getKeyValuePoint(points_dict,factor_key):
    return points_dict.get(factor_key,0)

# points range is a 2-dimensions list. 1st column and 2nd column are range, the 3rd column is value
def getRangePoint(points_range,factor):
    for i in range(len(points_range)):
        if factor in range(points_range[i][0], points_range[i][1]):
            return (points_range[i][2])
    return 0


# points is a dict or a list including all points, and this function returns the all points sum 
def getTotalPoint(points):
    return_point=0
    if isinstance(points,dict):
        for point in points.values():
            return_point+=point
    elif isinstance(points,list):
        for point in points:
            return_point+=point
    else:
        return_point=0
    return return_point