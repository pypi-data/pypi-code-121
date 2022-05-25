"""standard error metric calculation functions"""


def pe(forecast, actual):
    """percentage forecast error"""
    if (actual == 0) & (forecast == 0):
        pe = 0
    elif forecast == 0:
        pe = -1
    elif actual == 0:
        pe = 1
    else:
        pe = (forecast - actual)/actual
    return round(100 * pe, 1)


def ape(forecast, actual):
    """absolute percentage forecast error"""
    if (actual == 0) & (forecast == 0):
        ape = 0
    elif forecast == 0:
        ape = 1
    elif actual == 0:
        ape = 1
    else:
        ape = abs((forecast - actual)/actual)
    return round(100 * ape, 1)


def wmape(forecast, actual):
    """weighted mean absolute percentage error"""
    wmape = sum(abs(forecast-actual))/sum(actual)
    return round(100 * wmape, 1)