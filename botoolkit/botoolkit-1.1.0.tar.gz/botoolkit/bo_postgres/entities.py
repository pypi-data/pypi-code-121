from typing import (
    List,
    Optional,
)


class WebBBDBImageBuild:
    """
    Сборка базового образа базы данных
    """

    def __init__(
        self,
        image_repository: str,
        base_image_name: str,
        commands: List[str],
        image_tag: str = 'latest',
        web_bb_app_branch: str = 'default',
        web_bb_core_branch: str = 'default',
        web_bb_accounting_branch: Optional[str] = None,
        web_bb_salary_branch: Optional[str] = None,
        web_bb_vehicle_branch: Optional[str] = None,
        web_bb_food_branch: Optional[str] = None,
        activated_plugins: List[str] = None,
    ):
        self._image_repository = image_repository
        self._image_tag = image_tag

        self._base_image_name = base_image_name

        self._web_bb_app_branch = web_bb_app_branch
        self._web_bb_core_branch = web_bb_core_branch
        self._web_bb_accounting_branch = web_bb_accounting_branch
        self._web_bb_salary_branch = web_bb_salary_branch
        self._web_bb_vehicle_branch = web_bb_vehicle_branch
        self._web_bb_food_branch = web_bb_food_branch
        self._activated_plugins = activated_plugins

        self._commands = commands

    def __repr__(self):
        """
        Человекочитаемое представление объекта
        """
        properties = ', '.join([f'{k}="{v}"' for k, v in self.as_dict().items()])

        return f'<WebBBDBImageBuild {properties}>'

    def __str__(self):
        return self.__repr__()

    @property
    def image_repository(self):
        return self._image_repository

    @property
    def image_tag(self):
        return self._image_tag

    @property
    def base_image_name(self):
        return self._base_image_name

    @property
    def web_bb_app_branch(self):
        return self._web_bb_app_branch

    @property
    def web_bb_core_branch(self):
        return self._web_bb_core_branch

    @property
    def web_bb_accounting_branch(self):
        return self._web_bb_accounting_branch

    @property
    def web_bb_salary_branch(self):
        return self._web_bb_salary_branch

    @property
    def web_bb_vehicle_branch(self):
        return self._web_bb_vehicle_branch

    @property
    def web_bb_food_branch(self):
        return self._web_bb_food_branch

    @property
    def activated_plugins(self):
        return self._activated_plugins

    @property
    def commands(self):
        return self._commands

    def as_dict(self):
        """
        Возвращает представление объекта в виде словаря
        """
        return {
            'image_repository': self._image_repository,
            'image_tag': self._image_tag,
            'base_image_name': self._base_image_name,
            'web_bb_app_branch': self._web_bb_app_branch,
            'web_bb_core_branch': self._web_bb_core_branch,
            'web_bb_accounting_branch': self._web_bb_accounting_branch,
            'web_bb_salary_branch': self._web_bb_salary_branch,
            'web_bb_vehicle_branch': self._web_bb_vehicle_branch,
            'web_bb_food_branch': self._web_bb_food_branch,
            'activated_plugins': (
                ','.join(
                    [
                        plugin.value
                        for plugin in self._activated_plugins
                    ]
                )
            ),
            'command': f'bash -c \'{" && ".join(self._commands)}\'',
        }
