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

def arc_sin(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    else:
        Arcsin = np.arcsin(angle)
        return Arcsin

def arc_cos(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    else:
        Arccos = np.arccos(angle)
        return Arccos

def arc_tan(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    else:
        Arctan = np.arctan(angle)
        return Arctan

def arc_cosec(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    else:
        try:
            Arccosec = 1/np.arcsin(angle)
            return Arccosec
        except ZeroDivisionError as error:
            return error

def arc_sec(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    else:
        Arcsec = 1/np.arccos(angle)
        return Arcsec

def arc_cot(angle):
    if angle == str(angle):
        raise TypeError(f"Invalid input! expected an integer value but got string {angle}")
    else:
        try:
            Arccot = np.arccos(angle)/np.arcsin(angle)
            return Arccot
        except ZeroDivisionError as error:
            return error
