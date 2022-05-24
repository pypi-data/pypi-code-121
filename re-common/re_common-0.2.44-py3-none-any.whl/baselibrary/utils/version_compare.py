def compare(a: str, b: str):
    '''
    比较两个版本的大小，需要按.分割后比较各个部分的大小
    :return 返回较大的版本号
    '''
    lena = len(a.split('.'))  # 获取版本字符串的组成部分
    lenb = len(b.split('.'))
    a2 = a + '.0' * (lenb-lena)  # b比a长的时候补全a
    b2 = b + '.0' * (lena-lenb)
    for i in range(max(lena, lenb)):  # 对每个部分进行比较，需要转化为整数进行比较
        if int(a2.split('.')[i]) > int(b2.split('.')[i]):
            return a
        elif int(a2.split('.')[i]) < int(b2.split('.')[i]):
            return b
        else:						# 比较到最后都相等，则返回第一个版本
            if i == max(lena, lenb)-1:
                return a


def compare_bool(a: str, b: str):
    '''
    比较两个版本的大小，需要按.分割后比较各个部分的大小
    :return 如果 a >= b 返回true
    '''
    lena = len(a.split('.'))  # 获取版本字符串的组成部分
    lenb = len(b.split('.'))
    a2 = a + '.0' * (lenb-lena)  # b比a长的时候补全a
    b2 = b + '.0' * (lena-lenb)
    for i in range(max(lena, lenb)):  # 对每个部分进行比较，需要转化为整数进行比较
        if int(a2.split('.')[i]) > int(b2.split('.')[i]):
            return True
        elif int(a2.split('.')[i]) < int(b2.split('.')[i]):
            return False
        else:						# 比较到最后都相等，则返回第一个版本
            if i == max(lena, lenb)-1:
                return True
