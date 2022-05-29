import sys

def jp(input_num):
    """Generate Japanese numeral format string.

    Args:
        input_num (str, int, float): target number

    Returns:
        str: Generated string.
    """
    return num2cnum(
        input_num,
        [
            None, None, None, '万',
            None, None, None, '億',
            None, None, None, '兆',
            None, None, None, '京',
            None, None, None, '垓',
            None, None, None, '𥝱',
            None, None, None, '穣',
            None, None, None, '溝',
            None, None, None, '澗',
            None, None, None, '正',
            None, None, None, '載',
            None, None, None, '極',
            None, None, None, '恒河沙',
            None, None, None, '阿僧祇',
            None, None, None, '那由他',
            None, None, None, '不可思議',
            None, None, None, '無量大数'
        ],
        [
            '分', '厘', '毛', '糸', '忽'
        ]
    )

def scn(input_num):
    """Generate simplified Chinese numeral format string.

    Args:
        input_num (str, int, float): target number

    Returns:
        str: Generated string.
    """
    return num2cnum(
        input_num,
        [
            None, None, None, '万',
            None, None, None, '亿',
            None, None, None, '兆',
            None, None, None, '京',
            None, None, None, '垓',
            None, None, None, '秭',
            None, None, None, '穰',
            None, None, None, '沟',
            None, None, None, '涧',
            None, None, None, '正',
            None, None, None, '载',
            None, None, None, '极',
            None, None, None, '恒河沙',
            None, None, None, '阿僧祇',
            None, None, None, '那由他',
            None, None, None, '不可思议',
            None, None, None, '无量大数'
        ],
        [
            '分', '厘', '毫', '丝', '忽'
        ]
    )

def tcn(input_num):
    """Generate traditional Chinese numeral format string.

    Args:
        input_num (str, int, float): target number

    Returns:
        str: Generated string.
    """
    return num2cnum(
        input_num,
        [
            None, None, None, '萬',
            None, None, None, '億',
            None, None, None, '兆',
            None, None, None, '京',
            None, None, None, '垓',
            None, None, None, '秭',
            None, None, None, '穣',
            None, None, None, '溝',
            None, None, None, '澗',
            None, None, None, '正',
            None, None, None, '載',
            None, None, None, '極',
            None, None, None, '恆河沙',
            None, None, None, '阿僧祇',
            None, None, None, '那由他',
            None, None, None, '不可思議',
            None, None, None, '無量大數'
        ],
        [
            '分', '厘', '毫', '絲', '忽'
        ]
    )

def kn(input_num):
    """Generate Korean numeral format string.

    Args:
        input_num (str, int, float): target number

    Returns:
        str: Generated string.
    """
    return num2cnum(
        input_num,
        [
            None, None, None, '만',
            None, None, None, '억',
            None, None, None, '조',
            None, None, None, '경',
            None, None, None, '해',
            None, None, None, '자',
            None, None, None, '양',
            None, None, None, '구',
            None, None, None, '간',
            None, None, None, '정',
            None, None, None, '재',
            None, None, None, '극',
            None, None, None, '항하사',
            None, None, None, '아승기',
            None, None, None, '나유타',
            None, None, None, '불가사의',
            None, None, None, '무량대수'
        ],
        [
            '分', '厘', '毛', '糸', '忽'
        ]
    )

def num2cnum(input_num, integer_numerals, decimal_numerals):
    """Generate various numeral format string.

    Args:
        input_num (str, int, float): target number
        integer_numerals (list): check README.md
        decimal_numerals (list): check README.md

    Returns:
        str: Generated string.
    """
    if (type(input_num) is int) or (type(input_num) is float):
        input_str = str(input_num)
    elif (type(input_num) is str):
        try:
            float(input_num)
        except ValueError:
            print('[ERROR] "%s" is not number.' % input_num)
            sys.exit()
        input_str = input_num
    else:
        print('[ERROR] cnum just supports following types: str or int or float')
        sys.exit()
    
    out_str = ''

    integer_str = input_str.split('.')[0]
    cnt = 0
    for i in range(len(integer_str)):
        out_str = integer_str[len(integer_str)-i-1] + out_str
        cnt = cnt + 1
        if i >= len(integer_numerals):
            continue
        if integer_numerals[i] != None:
            if int(out_str[0:cnt]) == 0:
                out_str = out_str[cnt+1:]
            if len(integer_str) != i + 1:
                out_str = integer_numerals[i] + out_str.lstrip('0')    
            cnt = 0

    # input data is integer.
    if len(input_str.split('.')) == 1:
        return out_str

    # input data is decimal.
    else:
        if out_str == '0':
            out_str = ''
        else:
            out_str = out_str + ' '
        
        float_str = input_str.split('.')[1]
        tmp = ''
        for i in range(len(float_str)):
            if i >= len(decimal_numerals):
                continue
            if decimal_numerals[i] == None:
                tmp = tmp + float_str[i]
            else:
                tmp = tmp + float_str[i]
                if int(tmp) != 0:
                    out_str = out_str + tmp.lstrip('0') + decimal_numerals[i]
                tmp = ''
        return out_str
