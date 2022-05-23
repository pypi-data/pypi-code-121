import numpy as np

def sin(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string value: {angle}")
    else:
        Sin = np.sin(angle)
        return round(Sin,3)

def cos(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string value: {angle}")
    else:
        Cos = np.cos(angle)
        return round(Cos,3)

def tan(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string value: {angle}")
    else:
        Tan = np.tan(angle)
        return round(Tan,3)

def sec(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string: {angle}")
    else:
        Sec = 1/np.cos(angle)
        return round(Sec,3)

def cosec(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string: {angle}")
    else:
        Cosec = 1/np.sin(angle)
        return round(Cosec,3)

def cot(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    elif angle == 0:
       raise ZeroDivisionError(f"Can't Divide the numerator by: {angle}")
    else:
        Cot = np.cos(angle)/np.sin(angle)
        return round(Cot,3)
