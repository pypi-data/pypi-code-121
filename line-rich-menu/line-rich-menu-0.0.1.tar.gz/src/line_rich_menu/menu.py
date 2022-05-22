from logging import getLogger
from os import environ
from typing import Optional, Any, Dict

import dotenv
import magic
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize

from .helper import validate_rich_menu_object
from .const import ACCESS_TOKEN_KEY, NO_TOKEN_TEXT


class LineRichMenu:
    def __init__(self, token: Optional[str] = None):
        self.token = token or environ.get(ACCESS_TOKEN_KEY)
        if self.token is None:
            self.logger.warning(NO_TOKEN_TEXT)
            exit(1)
        self.client = LineBotApi(self.token)

    @property
    def logger(self):
        return getLogger(self.__class__.__name__)

    def create_menu(
        self, data: Dict[str, Any], image_path: str, set_default: bool = False
    ):
        """

        :param set_default:
        :param data:
        :param image_path:
        :return:
        """
        mime = magic.from_file(image_path, mime=True)
        valid = validate_rich_menu_object(token=self.token, obj=data)

        if not valid:
            self.logger.error(
                "Invalid menu object, see https://developers.line.biz/en/reference/messaging-api/#rich-menu-object"
            )
            exit(1)

        if mime not in ["image/jpeg", "image/png"]:
            self.logger.error(
                "Invalid image file type, only PNG and JPG are supported. "
                "See https://developers.line.biz/en/reference/messaging-api/#upload-rich-menu-image"
            )
            exit(1)

        m = RichMenu(
            size=RichMenuSize(
                width=data["size"]["width"], height=data["size"]["height"]
            ),
            selected=set_default,  # override from data
            name=data["name"],
            chat_bar_text=data["chatBarText"],
            areas=data["areas"],
        )
        menu_id = self.client.create_rich_menu(rich_menu=m)

        with open(image_path, "rb") as img_file:
            self.client.set_rich_menu_image(
                rich_menu_id=menu_id, content_type=mime, content=img_file
            )

        if set_default:
            self.client.set_default_rich_menu(menu_id)

        return menu_id
