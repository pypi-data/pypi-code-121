import random


class RingList(object):
    def __init__(self):
        """
        环形列表初始化
        """
        self.objlist = list()
        # 列表中数据总量
        self.num = 0
        self.index = 0

    def append(self, p_object):
        """

        :param p_object: 增加到环形列表的元素
        :return:
        """
        self.num += 1
        self.objlist.append(p_object)

    def pop(self, index=None):
        """

        :param index: 如果给index值，将会返回固定的该索引位置的值；如果不给，将会循环输出该列表的值
        :return:
        """
        if self.num == 0:
            return None
        if index is not None:
            self.index = index
        obj = self.objlist[self.index % self.num]
        self.index += 1
        return obj

    def exist(self, mstring):
        """

        :param mstring: 需要验证是否存在的字符串
        :return:
        """
        if mstring:
            if mstring in self.objlist:
                return True
            else:
                return False
        else:
            print("传入的string为空的")
            return False

    def remove(self, mstring):
        """

        :param mstring: 需要删除的字符串
        :return:
        """
        if mstring:
            if mstring in self.objlist:
                self.objlist.remove(mstring)
                self.num = self.num - 1

    def length(self):
        """
        获取列表当前长度 及环型列表现在的长度
        :return:
        """
        return len(self.objlist)

    def get_random(self):
        """
        获取随机代理
        :return:
        """
        return random.choice(self.objlist)

# if __name__ == "__main__":
#     ringList = RingList()
#     for i in range(1,100):
#         ringList.append(i)
#     # print(ringList.objlist)
#     # print(ringList.num)
#     # print()
#     while True:
#         print(ringList.pop())
