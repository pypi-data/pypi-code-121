import math
from decimal import Decimal
from enum import Enum

class fraction(Enum):
    
    floor = 0
    """ 切り捨て """

    round = 1
    """ 四捨五入 """

    ceil = 2
    """ 切り上げ """
    
def round(val, f:fraction, digits = 0):
    
    # 返却値初期化
    retVal = 0
    
    # 端数調整用
    dd = 1
    ee = 0 if digits < 2 else Decimal('9' * digits - 1)
    if digits != 0:
        if digits > 0:
            for _ in range(digits) : dd *= Decimal(str(0.1))
        else:
            for _ in range(digits) : dd *= 10
            for _ in range(digits) : ee *= Decimal(str('0.1'))
    
    # Decimal型にキャスト
    dVal = Decimal(str(val))
    
    if f == fraction.floor:
        if dVal > 0:
            retVal = Decimal(math.floor(dVal))
        else:
            retVal = Decimal(math.floor(Decimal(str(dVal)) + Decimal(str(0.9))))
    elif f == fraction.round:
        if dVal > 0:
            retVal = Decimal(math.floor(Decimal(str(dVal)) + Decimal(str(0.5))))
        else:
            retVal = Decimal(math.floor(Decimal(str(dVal)) + Decimal(str(0.49))))
    elif f == fraction.ceil:
        if dVal > 0:
            retVal = Decimal(math.floor(Decimal(str(dVal)) + Decimal(str(0.9)) + Decimal(str(ee))))
        else:
            retVal = Decimal(math.floor(dVal))
    
    if digits != 0:
        retVal = retVal / dd
    
    # 戻り値を返す
    return retVal