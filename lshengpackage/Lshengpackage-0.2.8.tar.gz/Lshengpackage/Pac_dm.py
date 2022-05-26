# -*- coding: UTF-8 -*-

from Lshengpackage.Delay import Delay


class mouse:
    def __init__(self, dm_obj, start_time=0.3, end_time=0.7):
        self.__dm_obj = dm_obj
        self.start_time = start_time
        self.end_time = end_time

    def lClick(self):
        """
        左键点击
        """
        Delay.delay(self.start_time, self.end_time)
        self.__dm_obj.LeftClick()

    def rClick(self):
        """
        右键点击
        """
        Delay.delay(self.start_time, self.end_time)
        self.__dm_obj.RightClick()

    def move_lClick(self, int_x, int_y):
        """
        移动并点击
        """
        self.__dm_obj.MoveTo(int_x, int_y)
        Delay.delay(self.start_time, self.end_time)
        self.lClick()

    def move_double_click(self, int_x, int_y):
        """
        移动并双击
        """
        self.__dm_obj.MoveTo(int_x, int_y)
        Delay.delay(self.start_time, self.end_time)
        self.__dm_obj.LeftDoubleClick()


class color:
    def __init__(self, dm_obj):
        self.__dm_obj = dm_obj

    def find_color(self, int_x1, int_y1, int_x2, int_y2, color, sim=0.9, direct=0):
        # dir 整形数:查找方向 0: 从左到右,从上到下
        # 1: 从左到右,从下到上
        # 2: 从右到左,从上到下
        # 3: 从右到左,从下到上
        # 4：从中心往外查找
        # 5: 从上到下,从左到右
        # 6: 从上到下,从右到左
        # 7: 从下到上,从左到右
        # 8: 从下到上,从右到左
        dm_ret = self.__dm_obj.FindColor(int_x1, int_y1, int_x2, int_y2, color, sim, direct)
        return dm_ret

    def find_color_click(self, int_x1, int_y1, int_x2, int_y2, color, sim=0.9, direct=0):
        """
        找色 并 点击
        :param int_x1:
        :param int_y1:
        :param int_x2:
        :param int_y2:
        :param color: 色彩格式
        :param sim:
        :param direct:
        :return: 成功 1, 失败 0
        """
        dm_ret = self.__dm_obj.FindColor(int_x1, int_y1, int_x2, int_y2, color, sim, direct)
        if dm_ret[-1] == -1:
            return
        else:
            int_x = dm_ret[0]
            int_y = dm_ret[1]
            mouse(self.__dm_obj).move_lClick(int_x, int_y)
            return 1


class pic:
    def __init__(self, dm_obj):
        self.__dm_obj = dm_obj

    def find_pic(self, int_x1, int_y1, int_x2, int_y2, pic_name, delta_color='000000', sim=0.9, direct=0):
        # dir 整形数:查找方向 0: 从左到右,从上到下 1: 从左到右,从下到上 2: 从右到左,从上到下 3: 从右到左, 从下到上
        """
        找图
        :param int_x1:
        :param int_y1:
        :param int_x2:
        :param int_y2:
        :param pic_name:
        :param delta_color:
        :param sim:
        :param direct:
        :return: 成功 返回坐标, 失败 -1, -1, -1
        """
        dm_ret = self.__dm_obj.FindPicE(int_x1, int_y1, int_x2, int_y2, pic_name, delta_color, sim, direct)
        return dm_ret

    def find_pic_click(self, int_x1, int_y1, int_x2, int_y2, pic_name, delta_color='000000', sim=0.9, direct=0):
        """
        找图并点击
        :return: 成功 1, 失败 0
        """
        dm_ret = self.__dm_obj.FindPicE(int_x1, int_y1, int_x2, int_y2, pic_name, delta_color, sim, direct)
        if dm_ret[-1] == -1:
            return
        else:
            int_x = dm_ret[1]
            int_y = dm_ret[-1]
            mouse(self.__dm_obj).move_lClick(int_x, int_y)
            return 1


class word:
    def __init__(self, dm_obj):
        self.__dm_obj = dm_obj

    def find_word(self, int_x1, int_y1, int_x2, int_y2, str_name, color_format, sim=0.8):
        """
        找字
        """
        dm_ret = self.__dm_obj.FindStrFast(int_x1, int_y1, int_x2, int_y2, str_name, color_format, sim)
        return dm_ret

    def find_word_click(self, int_x1, int_y1, int_x2, int_y2, str_name, color_format, sim=0.8):
        """
        找字并点击
        :param int_x1:
        :param int_y1:
        :param int_x2:
        :param int_y2:
        :param str_name:
        :param color_format:
        :param sim:
        :return: 成功 1, 失败 0
        """
        dm_ret = self.__dm_obj.FindStrFast(int_x1, int_y1, int_x2, int_y2, str_name, color_format, sim)
        if dm_ret[-1] == -1:
            return
        else:
            int_x = dm_ret[0]
            int_y = dm_ret[1]
            mouse(self.__dm_obj).move_lClick(int_x, int_y)
            return 1
