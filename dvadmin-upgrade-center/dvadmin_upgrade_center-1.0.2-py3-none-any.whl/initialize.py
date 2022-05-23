# 初始化
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()
from dvadmin.utils.core_initialize import CoreInitialize

from dvadmin.system.models import Menu, MenuButton, Dictionary

from .init_data import (
    menu_data,
    menu_button_data,
    dictionary_data,
)


class Initialize(CoreInitialize):
    creator_id = 1

    def init_menu(self):
        """
        初始化菜单表
        """
        self.menu_data = menu_data
        self.save(Menu, self.menu_data, "菜单表")

    def init_menu_button(self):
        """
        初始化菜单权限表
        """
        self.menu_button_data = menu_button_data
        self.save(MenuButton, self.menu_button_data, "菜单权限表")

    def init_dictionary(self):
        """
        初始化字典表
        """
        data = dictionary_data
        self.save(Dictionary, data, "字典表", no_reset=False)

    def run(self):
        self.init_menu()
        self.init_menu_button()


# 项目init 初始化，默认会执行 main 方法进行初始化
def main(reset=False):
    Initialize(reset).run()
    pass


if __name__ == '__main__':
    main()
