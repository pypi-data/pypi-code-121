import numba

@numba.njit('b1(f8,f8,f8[:,:])')
def ray_tracing(x,y,poly):
    ''' 
    2D Ray tracing algorithm that tests if a point is inside the poly(gon) coordinates given
    
    Arguments:
    - x: x coordinates (general)
    - y: y coordinates (general)
    - poly: polygon corners
    
    Returns:
    - boolean
    '''
    n = len(poly)
    inside = False
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside