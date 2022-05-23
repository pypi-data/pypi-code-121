import math

def to_str_milles(value,order,symbol,nb):
    bf      = str(value)[::-1][:order][::-1]
    af      = str(value)[::-1][order:][::-1]
    laf     = len(af)
    vf      = float(value[:laf] + '.' + value[laf:laf + nb + 1])
    vf      = number_lib.myround(vf,nb)
    value   = str(vf) + 'M'
    return value


def myround(n,nb=0,toInt=True,toStr=False):
    value = n
    if n == 0:  return 0
    try:
        if nb == 0:
            value = int(n)
            return value

        sgn   = -1 if n < 0 else 1
        k     = -math.floor(math.log10(abs(n)))
        scale = int(k) + nb - 1
        if scale <= 0:
            scale = 1
        factor = 10**scale
        value = sgn*math.floor(abs(n)*factor)/factor
    except:
        pass

    if toInt:
        value_str              = str(value) if '.' in str(value) else '%s.'%value
        decimal                = len(value_str.replace('-','').split('.')[0])
        if decimal != 1:
            try:
                value = int(value)
            except:
                pass

    if toStr:
        value   = str(value)
        if len(value) >= 12:
            value   = to_str_milles(value,12,'G',nb)
        elif len(value) >= 8:
            value   = to_str_milles(value,8,'M',nb)
        elif len(value) >= 4:
            value   = to_str_milles(value,4,'k',nb)
    return value