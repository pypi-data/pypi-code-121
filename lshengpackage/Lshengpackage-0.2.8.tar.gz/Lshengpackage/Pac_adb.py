# -*- coding:utf-8 -*-
# !/usr/bin/env python
import sys
from time import sleep
import numpy as np
from PIL import ImageFile
from PIL import Image
from cv2 import cv2
import os
import aircv as ac

# 全局路径
path = sys.path[0]

pic_path = sys.path[0] + "\\pic\\"  # 文件夹名称请自行修改

# #图片文件
# shot_pic = "shot_pic.png" #截图文件
scr = "full.png"

adb_shell = "adb shell /system/bin/screencap -p ../sdcard/"

adb_pull = "adb pull /sdcard/"


class Mouse:

    def tap_work(self, x, y):
        os.system('adb shell input tap {} {}'.format(x, y))

    def swip_work(self, x, y, x2, y2):
        os.system('adb shell input swipe {} {} {} {}'.format(x, y, x2, y2))


class Pic(Mouse):

    def cut_pic(self, pic_name):
        # 屏幕截图，默认存放到当前根目录picture文件夹下，请转public自行修改path路径
        # pic_name:屏幕截图生成名称
        os.system("%s%s" % (adb_shell, pic_name))
        os.system("%s%s %s%s" % (adb_pull, pic_name, path, pic_name))
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def save_bmp(self, pic_name, int_x1, int_y1, int_x2, int_y2):
        """截图保存"""

        self.cut_pic(pic_name)
        img = Image.open(path + pic_name)
        # (4)将图片验证码截取
        code_image = img.crop((int_x1, int_y1, int_x2, int_y2))
        code_image.save(path + pic_name)  # 截取的验证码图片保存为新的文件

    def find_pic(self, pic_name, int_x1, int_y1, int_x2, int_y2, lcons):  # 从table桌面Icons图标查找，如果有则返回其坐标位置
        # pic_name：屏幕截图生成名称 int_x1, int_y1, int_x2, int_y2提取屏幕的点坐标为左上角何右下角的点坐标
        # lcons:需要找的图片名称
        self.save_bmp(pic_name, int_x1, int_y1, int_x2, int_y2)
        yuan = cv2.imdecode(np.fromfile(path + pic_name, dtype=np.uint8), -1)
        mubi = cv2.imdecode(np.fromfile(path + lcons, dtype=np.uint8), -1)  # 读取中文路径及名称
        result = ac.find_template(yuan, mubi, 0.7)  # 0.7相似度
        if result is not None:
            return result['result'][0], result['result'][1]
        # return yuan.shape[1],yuan.shape[0]
        else:
            # print("没找到")
            return None

    def del_pic(self, my_file):  # 删除照片
        if os.path.exists(path + my_file):  # 如果文件存在
            # 删除文件，可使用以下两种方法。
            os.remove(path + my_file)
            # os.unlink(path)
        else:
            print('no such file:%s' % my_file)  # 则返回文件不存在

    def find_pic_click(self, scr_name, int_x1, int_y1, int_x2, int_y2, lcons):  # 找图单击,找不到返回为空
        get = self.find_pic(scr_name, int_x1, int_y1, int_x2, int_y2, lcons)
        if get is not None:
            get = self.find_pic(scr_name, int_x1, int_y1, int_x2, int_y2, lcons)
            m = list(get)
            self.tap_work(m[0], m[1])
        else:
            return None

    def find_pic_daubleclick(self, scr_name, int_x1, int_y1, int_x2, int_y2, lcons):  # 找图双击，找不到返回为空
        get = self.find_pic(scr_name, int_x1, int_y1, int_x2, int_y2, lcons)
        if get is not None:
            get = self.find_pic(scr_name, int_x1, int_y1, int_x2, int_y2, lcons)
            n = list(get)
            self.tap_work(n[0], n[1])
            sleep(0.2)
            self.tap_work(n[0], n[1])
        else:
            return None
