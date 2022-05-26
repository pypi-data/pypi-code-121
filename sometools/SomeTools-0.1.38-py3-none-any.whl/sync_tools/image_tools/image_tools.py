import os
import random
from sometools.sync_tools.base import Base
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class ImageMixin(Base):
    """
    https://pillow.readthedocs.io/en/stable/
    """

    def __init__(self, *args, **kwargs):
        super(ImageMixin, self).__init__(*args, **kwargs)

    @staticmethod
    def img_blurred(img_path: str) -> str:
        """
        :param img_path: 原始图片路径
        :return: 模糊后图片路径
        """
        if img_path:
            dir_path, file_ext_name = os.path.splitext(img_path)
            im = Image.open(img_path)
            im2 = im.filter(ImageFilter.BLUR)
            _new_img_path = dir_path+'img_blurred'+file_ext_name
            im2.save(_new_img_path, 'jpeg')
            return _new_img_path
        else:
            return ''

    @staticmethod
    def img_generate_verification_code(font_path: str, img_path: str) -> tuple:
        """
        生成四字验证码
        :param font_path: 字体文件路径
        :param img_path: 保存图片路径
        :return: 验证码内容中的四个字母, 四个字母组成的验证码图片
        """

        # 随机字母:
        def rndChar():
            return chr(random.randint(65, 90))

        # 随机颜色1:
        def rndColor():
            return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

        # 随机颜色2:
        def rndColor2():
            return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

        # 240 x 60:
        width = 60 * 4
        height = 60
        image = Image.new('RGB', (width, height), (255, 255, 255))
        # 创建Font对象:
        font = ImageFont.truetype(font_path, 36)
        import os
        os.getcwd()
        # 创建Draw对象:
        draw = ImageDraw.Draw(image)
        # 填充每个像素:
        for x in range(width):
            for y in range(height):
                draw.point((x, y), fill=rndColor())
        # 输出文字:
        _temp_str = ''
        for t in range(4):
            _sin_str = rndChar()
            _temp_str += _sin_str
            draw.text((60 * t + 10, 10), _sin_str, font=font, fill=rndColor2())
        # 模糊:
        image = image.filter(ImageFilter.BLUR)
        _output_path_str = _temp_str+'.jpg'
        if img_path:
            _output_path_str = img_path + 'code.jpg'
        image.save(_output_path_str, 'jpeg')
        return _temp_str, _output_path_str
