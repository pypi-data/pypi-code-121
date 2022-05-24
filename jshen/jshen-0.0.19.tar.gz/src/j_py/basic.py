# _*_coding     : UTF_8_*_
# Author        :Jie Shen
# CreatTime     :2022/2/2 10:37

"""
基础类型的扩展：list,str
"""


def list_mul(l1, l2):
    """
    列表乘法
    :param l1:
    :param l2:
    :return:
    """
    if len(l1) != len(l2):
        raise "len(l1) != len(l2)"
    products = []
    for n1, n2 in zip(l1, l2):
        products.append(n1 * n2)
    return products


def list_add(l1, l2):
    """
    列表加法
    :param l1:
    :param l2:
    :return:
    """
    products = []
    if type(l2) is not list:
        # 支持广播加法
        for n1 in l1:
            products.append(n1+l2)
        return products

    if len(l1) != len(l2):
        raise "len(l1) != len(l2)"
    for n1, n2 in zip(l1, l2):
        products.append(n1 + n2)
    return products
