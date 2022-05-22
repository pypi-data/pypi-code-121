def getItemByFieldValue(arr: [], fieldname: str, fieldvalue) -> object:
    '''
    根据数组中某个item的值，返回该Item，如果数组中有多个Item，返回第一个，如果要返回所有Item，请使用getItemsByFieldValue

    :param arr: 数组，里面应该都是dict
    :param fieldname: 字段名
    :param fieldvalue: 字段值
    :return:
    '''
    for item in arr:
        if item[fieldname] == fieldvalue:
            return item

    return None


def getItemsByFieldValue(arr: [], fieldname: str, fieldvalue) -> []:
    '''
    根据数组中某个item的值，返回该Item组成的列表

    :param arr: 数组，里面应该都是dict
    :param fieldname: 字段名
    :param fieldvalue: 单个字段值,目前支持int,str,float,bool, 如字段值为多个，可用数组，例如：[1,2,3], ["a","b","c"]
    :return: 数组
    '''
    fields = []
    tmp = []
    if isinstance(fieldvalue, list):
        fields = fieldvalue
    elif isinstance(fieldvalue, (int, str, float, bool)):
        fields.append(fieldvalue)

    for field in fields:
        for item in arr:
            if item[fieldname] == field:
                tmp.append(item)

    return tmp


def collectionFieldToStr(arr: [], fieldname: str, sep: str = ",") -> str:
    '''
    收集数组中的dict中的某个值，并将其连接到一个字符串中

    :param arr: 带dict的数组
    :param fieldname: 字段名
    :param sep: 分隔符，默认为“，”
    :return: 拼接好的字符串
    '''
    tmp = []
    for item in arr:
        tmp.append(item[fieldname])

    return sep.join(map(str, tmp))


if __name__ == '__main__':
    # a = getItemsByFieldValue([{"name": "北京", "value": 1}, {"name": "北京2", "value": 1}, {"name": "北京3", "value": 1}, ],
    #                          "name", 1)
    a = collectionFieldToStr([{"name": "北京", "value": 1}, {"name": "北京2", "value": 1}, {"name": "北京3", "value": 1}],
                             "value")
    print(a)
