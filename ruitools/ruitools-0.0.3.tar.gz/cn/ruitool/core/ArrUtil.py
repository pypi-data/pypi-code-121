def getItemByFieldValue(list: [], fieldname: str, fieldvalue) -> object:
    '''
    根据数组中某个item的值，返回该Item，如果数组中有多个Item，返回第一个，如果要返回所有Item，请使用getItemsByFieldValue

    :param list: 数组，里面应该都是dict
    :param fieldname: 字段名
    :param fieldvalue: 字段值
    :return:
    '''
    for item in list:
        if item[fieldname] == fieldvalue:
            return item

    return None


def getItemsByFieldValue(list: [], fieldname: str, fieldvalue) -> []:
    '''
    根据数组中某个item的值，返回该Item组成的列表

    :param list: 数组，里面应该都是dict
    :param fieldname: 字段名
    :param fieldvalue: 字段值
    :return:
    '''
    tmp = []
    for item in list:
        if item[fieldname] == fieldvalue:
            tmp.append(item)

    return tmp
