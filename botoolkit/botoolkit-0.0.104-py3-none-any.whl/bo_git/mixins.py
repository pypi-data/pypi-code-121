from typing import (
    List,
)

from botoolkit.bo_git.strings import (
    EMPTY_APP_BRANCH_ERROR,
    EMPTY_CORE_BRANCH_ERROR,
    EMPTY_DEPENDENCY_PROJECT_BRANCH_ERROR,
    EMPTY_PROJECTS_BRANCHES_ERROR,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)


class WebBBAppBranchArgumentMixin:
    """
    Добавляет параметры
        --web_bb_app_branch
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'web_bb',
                    'option': 'app_branch',
                    'help': 'Используемая ветка web_bb_app',
                },
            )
        )


class WebBBProjectsArgumentsMixin:
    """
    Добавляет параметры
        --web_bb_accounting_branch
        --web_bb_salary_branch
        --web_bb_vehicle_branch
        --web_bb_food_branch
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._projects_combination: List[ProjectEnum] = []

        super().__init__(
            *args,
            **kwargs,
        )

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'web_bb',
                    'option': 'accounting_branch',
                    'help': 'Используемая ветка web_bb_accounting',
                },
                {
                    'section': 'web_bb',
                    'option': 'salary_branch',
                    'help': 'Используемая ветка web_bb_salary',
                },
                {
                    'section': 'web_bb',
                    'option': 'vehicle_branch',
                    'help': 'Используемая ветка web_bb_vehicle',
                },
                {
                    'section': 'web_bb',
                    'option': 'food_branch',
                    'help': 'Используемая ветка web_bb_food',
                },
            )
        )

    def _validate_web_bb_accounting_branch(self):
        if self._parsed_args.web_bb_accounting_branch:
            self._projects_combination.append(ProjectEnum.WEB_BB_ACCOUNTING)

    def _validate_web_bb_salary_branch(self):
        if self._parsed_args.web_bb_salary_branch:
            self._projects_combination.append(ProjectEnum.WEB_BB_SALARY)

    def _validate_web_bb_vehicle_branch(self):
        if self._parsed_args.web_bb_vehicle_branch:
            self._projects_combination.append(ProjectEnum.WEB_BB_VEHICLE)

    def _validate_web_bb_food_branch(self):
        if self._parsed_args.web_bb_food_branch:
            self._projects_combination.append(ProjectEnum.WEB_BB_FOOD)


class WebBBBranchesArgumentsMixin(
    WebBBAppBranchArgumentMixin,
    WebBBProjectsArgumentsMixin,
):
    """
    Добавляет параметры
        --web_bb_app_branch
        --web_bb_core_branch
        --web_bb_accounting_branch
        --web_bb_salary_branch
        --web_bb_vehicle_branch
        --web_bb_food_branch
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'web_bb',
                    'option': 'core_branch',
                    'help': 'Используемая ветка web_bb_core',
                },
            )
        )

    def _validate_branches(self):
        """
        Валидация веток проектов
        """
        if (
            hasattr(self, '_allowed_empty_config_parameters') and
            self._allowed_empty_config_parameters != ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS  # noqa
        ):
            if not self._parsed_args.web_bb_app_branch:
                raise RuntimeError(EMPTY_APP_BRANCH_ERROR)

            if not self._parsed_args.web_bb_core_branch:
                raise RuntimeError(EMPTY_CORE_BRANCH_ERROR)

            projects = list(
                filter(
                    None,
                    [
                        self._parsed_args.web_bb_accounting_branch and ProjectEnum.WEB_BB_ACCOUNTING,  # noqa
                        self._parsed_args.web_bb_salary_branch and ProjectEnum.WEB_BB_SALARY,  # noqa
                        self._parsed_args.web_bb_vehicle_branch and ProjectEnum.WEB_BB_VEHICLE,  # noqa
                        self._parsed_args.web_bb_food_branch and ProjectEnum.WEB_BB_FOOD,  # noqa
                    ]
                )
            )

            if not any(projects):
                raise RuntimeError(EMPTY_PROJECTS_BRANCHES_ERROR)

            projects_dependencies = ProjectEnum.get_dependencies()
            errors = []

            for project in projects:
                if project in projects_dependencies:
                    for project_dependency in projects_dependencies[project]:
                        if project_dependency not in projects:
                            errors.append(
                                EMPTY_DEPENDENCY_PROJECT_BRANCH_ERROR.format(
                                    project_dependency.name,
                                    project.name,
                                )
                            )

            if errors:
                raise RuntimeError(
                    '\n'.join(errors)
                )

    def _validate_arguments(self):
        super()._validate_arguments()

        self._validate_branches()
