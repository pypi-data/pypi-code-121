import decimal


def half_round(num, fmt):
    """
    decimal_round(0.1235, '1.0') == 0.0
    decimal_round(0.1235, '0.1') == 0.1
    decimal_round(0.1235, '0.01') == 0.12
    decimal_round(0.1235, '0.001') == 0.124
    decimal_round(0.1235, '0.0001') == 0.1235
    """
    if fmt.find('.') >= 0:
        # Float
        n = decimal.Decimal(str(num)).quantize(decimal.Decimal(fmt), rounding=decimal.ROUND_HALF_UP)
        return float(n)
    else:
        # Integer
        raise ValueError('Format not allowed')


def clear_int(num, clear_with):
    clear_with = int('1'.zfill(intlen(clear_with)))

    if intlen(num) == intlen(clear_with):
        raise ValueError('You can not clear same length integer')
    return num // clear_with * clear_with


def intlen(num):
    return len(str(num))


def num_to_percent(part, whole):
    if whole == 0:
        return 0
    elif part > whole:
        raise ValueError('part must be less than whole.')
    return 100 * float(part) / float(whole)


def percent_to_num(whole, percent):
    if whole == 0:
        return 0
    return float(percent * whole) / 100


def isint(some):
    try:
        int(some)
        return True
    except (ValueError, TypeError):
        return False
