from typing import Any
from PIL import Image, ImageDraw, ImageFont

from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.commmand.Command import Command


class ConvertTextToImage(Command):
    data: str
    image_path: str

    def __init__(self, data: str, image_path: str):
        self.data = data
        self.image_path = image_path

    def execute(self) -> Any:
        fontname = "DejaVuSansMono.ttf"
        fontsize = 14
        color_text = "black"
        color_background = "white"
        margin = 10

        text = self.data
        title = DI.get_server_name()
        font = ImageFont.truetype(fontname, fontsize)
        title_width, title_height, title_font = self._get_title_dimensions(title)
        width, height = self._get_size(text, font)
        h = height + title_height + margin
        w = (width if width > title_width else width) + margin
        img = Image.new("RGB", (w, h), color_background)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, w, title_height), outline="black", fill="black")
        d.text(((w/2)-(title_width/2), 1), title, fill="yellow", font=title_font)
        d.text((1, title_height + 1), text, fill=color_text, font=font)

        img.save(self.image_path)

    @staticmethod
    def _get_title_dimensions(title: str):
        fontname = "DejaVuSansMono.ttf"
        fontsize = 24

        font = ImageFont.truetype(fontname, fontsize)
        width, height = ConvertTextToImage._get_size(title, font)
        return width, height + 4, font

    @staticmethod
    def _get_size(txt, font):
        test_img = Image.new("RGB", (1, 1))
        test_draw = ImageDraw.Draw(test_img)
        return test_draw.textsize(txt, font)
