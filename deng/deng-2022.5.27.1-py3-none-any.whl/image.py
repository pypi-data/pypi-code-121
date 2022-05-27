#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
作者：dengqingyong
邮箱：yu12377@163.com
时间：2018/1/31 下午3:11
"""
from random import randint
from os.path import dirname, basename, join, exists
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    import os
    os.system('pip install Pillow')
    from PIL import Image, ImageDraw, ImageFont


class ImageTools(object):
    """图片处理工具"""

    @staticmethod
    def add_text_to_image(imagefile, texts, size=24, font='Comic Sans MS Bold.ttf'):
        """给图片添加文件水印，并返回一新文件名
            参数
            imagefile: 需要添加水印的图片
            texts：需要作为水印添加的文字
            size：水印文字的尺寸
            font：水印文字字体
        """
        image = Image.open(imagefile)
        try:
            font = ImageFont.truetype(font=font, size=size, encoding='unic')
        except Exception as e:
            print('找不到字体：{}'.format(font))
        draw = ImageDraw.Draw(image)
        if isinstance(texts, (list, tuple)):
            i = 20
            for text in texts:
                draw.text((50, i), text, (255, 0, 0), font=font)
                i += 20 + size
        else:
            draw.text((50, 50), texts, (255, 0, 0), font=font)
        while True:
            newfile = join(dirname(imagefile), '{}{}'.format(randint(10000000, 99999999), basename(imagefile)))
            if not exists(newfile):
                break
        image.save(newfile)
        return newfile
