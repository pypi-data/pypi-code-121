from typing import (
    Dict,
    List,
    Optional,
)

from botoolkit.bo_jenkins.consts import (
    STAND,
)
from botoolkit.bo_jenkins.helpers import (
    StandConfiguration,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
)
from botoolkit.core.consts import (
    TAB_SPACES,
)


class JenkinsGroovyScriptsGenerator:
    """
    Генератор Groovy скриптов для создания интерфейса Databaser в Jenkins
    """
    def __init__(
        self,
        stands_configurations: List[StandConfiguration],
    ):
        self._stand_configurations = stands_configurations

        self._generated_code: Dict[str, str] = {}

    def _generate_stands_urls_list(self):
        """
        Генерация списка URL-ов активных тестовых стендов
        """
        print(f'\n{STAND} parameter\n')

        lines = [
            'return [',
        ]

        for stand_configuration in self._stand_configurations:
            lines.append(f'{TAB_SPACES}\'{stand_configuration.url}\',')

        lines.append(']')

        code = '\n'.join(lines)

        print(code)

        self._generated_code[STAND] = code

    def _generate_select_branch_script(
        self,
        parameter_name: str,
        project: Optional[ProjectEnum] = None,
        with_none: bool = True,
    ):
        """
        Генерация списка допустимых веток для выбранного проекта для каждого
        стенда
        """
        print(f'\n{parameter_name} parameter\n')

        lines = []

        for inx, stand_configuration in enumerate(self._stand_configurations):
            if project in (ProjectEnum.WEB_BB_APP, ProjectEnum.WEB_BB_CORE):
                branch = f'"{stand_configuration.branch}"'
            else:
                branch = (
                    f'"{stand_configuration.branch}"' if
                    project in stand_configuration.projects else
                    ''
                )

                if with_none:
                    if branch:
                        branch = f'"", {branch}'
                    else:
                        branch = '""'

            else_ = 'else ' if inx != 0 else ''

            lines.append(
                f'{else_}if ({STAND}.equals("{stand_configuration.url}")) {{\n'
                f'    return [{branch}]\n'
                f'}}'
            )

        lines.append(
            f'else {{\n'
            f'    return ["error"]\n'
            f'}}'
        )

        code = '\n'.join(lines)

        print(code)

        self._generated_code[parameter_name] = code

    def get_code_by_parameter_name(
        self,
        parameter_name: str,
    ):
        """
        Возвращает сгенерированный Groovy-код параметра
        """
        return self._generated_code.get(parameter_name)

    def generate(self):
        """
        Генерация Groovy скриптов
        """
        self._generate_stands_urls_list()

        self._generate_select_branch_script(
            parameter_name='WEB_BB_APP_BRANCH',
            project=ProjectEnum.WEB_BB_APP,
            with_none=False,
        )

        self._generate_select_branch_script(
            parameter_name='WEB_BB_CORE_BRANCH',
            project=ProjectEnum.WEB_BB_CORE,
            with_none=False,
        )

        self._generate_select_branch_script(
            parameter_name='WEB_BB_ACCOUNTING_BRANCH',
            project=ProjectEnum.WEB_BB_ACCOUNTING,
        )

        self._generate_select_branch_script(
            parameter_name='WEB_BB_SALARY_BRANCH',
            project=ProjectEnum.WEB_BB_SALARY,
        )

        self._generate_select_branch_script(
            parameter_name='WEB_BB_VEHICLE_BRANCH',
            project=ProjectEnum.WEB_BB_VEHICLE,
        )

        self._generate_select_branch_script(
            parameter_name='WEB_BB_FOOD_BRANCH',
            project=ProjectEnum.WEB_BB_FOOD,
        )
