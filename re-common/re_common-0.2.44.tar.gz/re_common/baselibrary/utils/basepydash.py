import pydash
from pydash import without, py_, reject, power


class BasePyDash(object):

    @classmethod
    def find_index(cls, lists, callback):
        """
        lists = [
            {'name': 'Michelangelo', 'active': False},
            {'name': 'Donatello', 'active': False},
            {'name': 'Leonardo', 'active': True}
        ]
        通过callback 查找对应数据的索引,找的的第一个会被返回，
        索引从0开始，找不到返回-1
        :param lists:
        :param callback: callback的结果一般是个bool值
        # 第一种形式
        callback = lambda item: item['name'] == 'Leonardo'
        callback = lambda item, index: index == 3
        callback = lambda item, index, obj: obj[index]['active']
        # 浅属性风格
        在内部pydash.utilities.prop()用于创建回调
        callback=['active'] or 'active' or ['active',True]
        # deep 属性样式
        callback =  'location.city'
        :return: 索引或者-1
        """

        return pydash.find_index(lists, callback)

    @classmethod
    def map_(cls, lists, callback):
        """
        和 find_index 一样 只是返回的是数据而不是索引，且返回找到的全部
        没有找到的一项会返回None
        :param lists:
        :param callback:
        如果是给的字典map_(users, {'location': {'city': 'Florence'}}会返回true False的列表
        :return:
        """
        return pydash.map_(lists, callback)

    @classmethod
    def find_last_index(cls, lists, callback):
        """
        查找最后一个
        :param lists:
        :param callback:
        :return:
        """
        return pydash.find_last_index(lists, callback)

    @classmethod
    def get(cls, obj, path, default=None):
        """
        用. 获取多层字典的数据
        :return:
        """
        return pydash.get(obj, path, default)

    @classmethod
    def chain(cls, lists):
        """
        or
        from pydash import py_
        py_(lists)
        :param lists:
        :return:
        """
        pydash.chain(lists)
        return cls

    @classmethod
    def without(cls, array, *values):
        """
        without([1, 2, 3, 2, 4, 4], 2, 4)
        [1, 3]
        创建一个数组，删除所有已传递值的匹配项
        :return:
        """
        return without(array, *values)

    @classmethod
    def reject(cls,collection, predicate=None):
        """
        不接受某些条件
        reject([1, 2, 3, 4], lambda x: x >= 3)
        [1, 2]
        :param collection:
        :param predicate:
        :return:
        """
        return reject(collection, predicate=predicate)


    @classmethod
    def for_each(cls):
        """
        这里告诉你for-each 怎么用

        :return:
        """

        def echo(value): print(value)

        lazy = py_([1, 2, 3, 4]).for_each(echo)

        result = lazy.value()

    @classmethod
    def commit(cls):
        """
        提交链
        :return:
        """

        def echo(value): print(value)

        lazy = py_([1, 2, 3, 4]).for_each(echo)

        result = lazy.value()

        committed = lazy.commit()

        committed.value()

        # 相当于
        committed = py_(lazy.value())

    @classmethod
    def power(cls,x,n):
        """
        x的n次方
        :param x:
        :param n:
        :return:
        """


square_sum = py_().power(2).sum()
print(square_sum)
