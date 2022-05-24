def get_attrs(settings):
    """
    获取模块参数转换为字典
    :param settings:
    :return:
    """
    attr = {}
    for i in (dir(settings)):
        if i.isupper():
            attr[i] = getattr(settings,i)
    return attr