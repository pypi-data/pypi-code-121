# -*coding:utf-8 -*-
# !/usr/bin/env python
import os


class command:
    def dev(self):
        # 查看当前链接设备
        os.system('adb devices')

    def log(self):
        # 查看日志
        os.system('adb logcat')

    def kill(self):
        # 结束adb服务
        os.system('adb kill-server')

    def star(self):
        # 开始adb服务
        os.system('adb start-server')

    def install(self, apk_name):
        # 安装软件
        os.system('adb install -r %s.apk' % apk_name)

    def uninstall(self, apk_name):
        # 卸载
        os.system('adb uninstall %s.apk' % apk_name)

    def up(self, file_name, path_phone):
        # 上传SDCard/../..手机端路径
        os.system('adb push %s %s' % (file_name, path_phone))

    def down(self, file_name):
        # 下载
        os.system('adb uninstall %s' % file_name)

    def scr(self, pic_name):
        # 屏幕截图到手机根目录
        os.system('adb shell screencap /sdcard/%s.png' % pic_name)

    def video_scr(self, video_name):
        # 录屏，默认mp4格式
        os.system('adb shell screenrecord /sdcard/%s.mp4' % video_name)
