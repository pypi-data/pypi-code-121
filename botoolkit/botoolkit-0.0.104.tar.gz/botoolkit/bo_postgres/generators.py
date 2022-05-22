from argparse import (
    Namespace,
)
from pathlib import (
    Path,
)
from typing import (
    List,
    Optional,
    Tuple,
)

from configupdater import (
    ConfigUpdater,
)
from jenkins import (
    Jenkins,
)

from botoolkit.bo_conf.helpers import (
    get_stands_configs,
)
from botoolkit.bo_git.enums import (
    BranchEnum,
)
from botoolkit.bo_jenkins.enums import (
    StandStateEnum,
)
from botoolkit.bo_jenkins.parsers import (
    JenkinsJobParser,
)
from botoolkit.bo_postgres.entities import (
    WebBBDBImageBuild,
)
from botoolkit.bo_postgres.enums import (
    DBImageTypeEnum,
)
from botoolkit.bo_postgres.helpers import (
    generate_db_image_name,
    get_parent_projects_combination,
)
from botoolkit.bo_postgres.repositories import (
    WebBBDBImageBuildRepository,
)
from botoolkit.bo_web_bb.consts import (
    RUN_ETALON_WEB_BB_APP_CONTAINER_COMMANDS,
    RUN_WEB_BB_APP_CONTAINER_COMMANDS,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
    ProjectPluginEnum,
)
from botoolkit.core.loggers import (
    logger,
)


class WebBBDBImageConfigurationGenerator:
    """
    Генератор конфигурационного файла
    """

    def __init__(
        self,
        repository: WebBBDBImageBuildRepository,
        parsed_args: Namespace,
        projects: Optional[Tuple[ProjectEnum]] = None,
    ):
        self._projects = projects if projects else ProjectEnum.get_projects()
        self._repository = repository
        self._parsed_args = parsed_args

    def _prepare_base_db_images(self):
        """
        Подготовка параметров создания базовых образов БД
        """
        projects_combinations = ProjectEnum.get_projects_combinations(
            projects=self._projects,
        )

        for projects_combination in projects_combinations:
            parent_combination = get_parent_projects_combination(
                src_combination=projects_combination,
            )

            parent_image_name = (
                generate_db_image_name(
                    projects_combination=parent_combination,
                    type_=DBImageTypeEnum.BASE,
                ) if
                parent_combination else
                self._parsed_args.postgres_image
            )

            image_repository, image_tag = generate_db_image_name(
                projects_combination=projects_combination,
                type_=DBImageTypeEnum.BASE,
                split_tag=True,
            )

            image_build_parameters = {
                'image_repository': image_repository,
                'image_tag': image_tag,
                'base_image_name': parent_image_name,
                'activated_plugins': ProjectPluginEnum.get_projects_plugins(
                    projects_combination=projects_combination,
                    only_base=True,
                ),
                'commands': RUN_WEB_BB_APP_CONTAINER_COMMANDS,
            }

            for project in projects_combination:
                image_build_parameters[f'{project.value}_branch'] = (
                    self._parsed_args.base_images_branch.value
                )

            self._repository.add(
                WebBBDBImageBuild(
                    web_bb_app_branch=self._parsed_args.base_images_branch.value,
                    web_bb_core_branch=self._parsed_args.base_images_branch.value,
                    **image_build_parameters,
                )
            )

    def _prepare_regional_configs(
        self,
    ) -> List[Tuple[str, str, ConfigUpdater]]:
        """
        Подготовка региональных конфигов
        """
        regional_configs = []

        stand_configs = get_stands_configs(
            configurations_git_repository_url=(
                self._parsed_args.boconf_configurations_git_repository_url
            ),
            configurations_path=(
                Path(self._parsed_args.boconf_configurations_path)
            ),
        )

        stand_config_uuid_map = {
            stand_config.get(
                section='runtime',
                option='app_config_uuid',
            ).value: stand_config
            for _, stand_config in stand_configs
        }

        jenkins_server = Jenkins(
            url=self._parsed_args.jenkins_url,
            username=self._parsed_args.jenkins_username,
            password=self._parsed_args.jenkins_password,
        )

        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=jenkins_server,
        )

        jenkins_job_parser.parse()

        jenkins_stands = jenkins_job_parser.get_jobs_data_as_tuple(
            state=StandStateEnum.AVAILABLE,
        )

        for region_stand in jenkins_stands:
            try:
                config = stand_config_uuid_map[region_stand[3]]
            except KeyError as e:
                logger.write(
                    f'Configuration file by parameters "{region_stand}" '
                    f'not found!'
                )

                raise e

            regional_configs.append(
                (
                    config.get(
                        section='runtime',
                        option='app_region_abbreviation',
                    ).value,
                    region_stand[1],  # branch
                    config,
                )
            )

        return regional_configs

    def _prepare_regional_image_build_parameters(
        self,
        region: str,
        branch: str,
        projects_combination,
        plugins,
        db_image_type: DBImageTypeEnum,
        commands: List[str],
        with_test_plugins: bool = False,
        parent_image_name: Optional[str] = None,
    ):
        if not parent_image_name:
            parent_image_name = generate_db_image_name(
                projects_combination=projects_combination,
                type_=DBImageTypeEnum.BASE,
            )

        image_repository, image_tag = generate_db_image_name(
            projects_combination=projects_combination,
            type_=db_image_type,
            region=region,
            split_tag=True,
            tag=branch,
        )

        activated_plugins = (
            ProjectPluginEnum.get_filtered_plugins_for_projects_combination(
                projects_combination=projects_combination,
                plugins=plugins,
                with_test_plugins=with_test_plugins,
            )
        )

        image_build_parameters = {
            'image_repository': image_repository,
            'image_tag': image_tag,
            'base_image_name': parent_image_name,
            'activated_plugins': activated_plugins,
            'commands': commands,
            f'{ProjectEnum.WEB_BB_APP.value}_branch': branch,
            f'{ProjectEnum.WEB_BB_CORE.value}_branch': branch,
        }

        for project in projects_combination:
            image_build_parameters[f'{project.value}_branch'] = branch

        return image_build_parameters

    def _prepare_regional_image_builds(
        self,
        region: str,
        branch: str,
        config: ConfigUpdater,
    ):
        """
        Создание конфигов для сборок базовых образов баз данных региона
        """
        plugins = config.get(
            section='plugins',
            option='activated_plugins',
        ).value.strip().replace(' ', '').split(',')

        plugins = ProjectPluginEnum.get_enums_by_str_plugins(
            plugins=plugins,
            exclude_projects=self._parsed_args.exclude_projects,
        )

        projects = ProjectPluginEnum.get_projects_by_plugins(
            plugins=plugins,
        )

        if projects:
            projects_combinations = (
                ProjectPluginEnum.get_project_combination_by_plugins(
                    plugins=plugins,
                    exclude_projects=self._parsed_args.exclude_projects,
                )
            )

            for projects_combination in projects_combinations:
                regional_image_build_parameters = (
                    self._prepare_regional_image_build_parameters(
                        region=region,
                        branch=branch,
                        projects_combination=projects_combination,
                        plugins=plugins,
                        db_image_type=DBImageTypeEnum.BASE,
                        commands=RUN_WEB_BB_APP_CONTAINER_COMMANDS,
                    )
                )

                self._repository.add(
                    WebBBDBImageBuild(
                        **regional_image_build_parameters,
                    )
                )

                if self._parsed_args.with_test_databases:
                    parent_image_name = (
                        f'{regional_image_build_parameters["image_repository"]}:{regional_image_build_parameters["image_tag"]}'  # noqa
                    )

                    test_regional_image_build_parameters = (
                        self._prepare_regional_image_build_parameters(
                            region=region,
                            branch=branch,
                            projects_combination=projects_combination,
                            plugins=plugins,
                            db_image_type=DBImageTypeEnum.ETALON,
                            commands=RUN_ETALON_WEB_BB_APP_CONTAINER_COMMANDS,
                            with_test_plugins=True,
                            parent_image_name=parent_image_name,
                        )
                    )

                    self._repository.add(
                        WebBBDBImageBuild(
                            **test_regional_image_build_parameters,
                        )
                    )

    def _prepare_base_regional_db_images(self):
        """
        Подготовка параметров для создания региональных базовых образов баз
        данных
        """
        regional_configs = self._prepare_regional_configs()

        for region, branch, config in regional_configs:
            branch_enum = BranchEnum(branch)
            if branch_enum not in self._parsed_args.exclude_branches:
                self._prepare_regional_image_builds(
                    region=region,
                    branch=branch,
                    config=config,
                )

    def generate(self):
        """
        Генерация параметров сборок базовых образов БД
        """
        self._prepare_base_db_images()
        self._prepare_base_regional_db_images()
