import re
import time

import xml.etree.ElementTree as ET
from argparse import (
    Namespace,
)
from distutils.util import (
    strtobool,
)
from pathlib import (
    Path,
)
from typing import (
    Optional,
    Tuple,
)
from urllib.parse import (
    quote,
)

import jenkins
from jenkins import (
    Jenkins,
)

from botoolkit.bo_conf.api import (
    BOConfigGenerator,
)
from botoolkit.bo_conf.settings import (
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_databaser.mixins import (
    DatabaserGeneralArgumentsMixin,
)
from botoolkit.bo_databaser.settings import (
    TOOL_NAME as BODATABASER_TOOL_NAME,
)
from botoolkit.bo_jenkins.enums import (
    BuildResultEnum,
    StandStateEnum,
)
from botoolkit.bo_jenkins.generators import (
    JenkinsGroovyScriptsGenerator,
)
from botoolkit.bo_jenkins.helpers import (
    StandConfiguration,
    prettify_xml_element,
)
from botoolkit.bo_jenkins.mixins import (
    JenkinsDatabaserArgumentsMixin,
)
from botoolkit.bo_jenkins.parsers import (
    JenkinsJobParser,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_jira.api import (
    JiraAPIClient,
)
from botoolkit.bo_jira.consts import (
    JIRA_ENT_IDS_RE,
    JIRA_PROJECTS_CONFORMITY,
    JIRA_STAND_URL_RE,
)
from botoolkit.bo_jira.enums import (
    JiraBuildSlicingDBStatusEnum,
    JiraCustomFieldEnum,
)
from botoolkit.bo_jira.helpers import (
    prepare_jira_issue_url,
)
from botoolkit.bo_jira.settings import (
    TOOL_NAME as BOJIRA_TOOL_NAME,
)
from botoolkit.bo_telegram.helpers import (
    TelegramMessageSender,
)
from botoolkit.bo_telegram.settings import (
    TOOL_NAME as BOTELEGRAM_TOOL_NAME,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
    ProjectPluginEnum,
)
from botoolkit.bo_web_bb.exceptions import (
    AppConfigUUIDCanNotGetFromServer,
    AppConfigUUIDNotFound,
)
from botoolkit.core.commands import (
    BOConfiguredToolCommand,
    BOConfiguredToolConfigureCommand,
    BOConfiguredToolLister,
)
from botoolkit.core.consts import (
    ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS,
)
from botoolkit.core.loggers import (
    logger,
)


class ConfigureBOJenkinsCommand(
    JenkinsDatabaserArgumentsMixin,
    BOConfiguredToolConfigureCommand,
):
    """
    Команда конфигурирования инструмента bojenkins
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Configure bojenkins for working with Jenkins instance.'
        )

    def get_tool_name(self):
        return BOJENKINS_TOOL_NAME

    def get_allowed_empty_config_parameters(self):
        return ALLOWED_ALL_EMPTY_CONFIG_PARAMETERS

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOTOOLKIT_TOOL_NAME)

        return required_config_tool_names


class BOJenkinsStandsLister(
    BOConfiguredToolLister,
):
    """
    Команда получения списка активных тестовых стендов
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Command for getting list of stands urls and branches of Jenkins '
            'actively jobs of BO.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.append(BOJENKINS_TOOL_NAME)

        return required_config_tool_names

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        jenkins_server = jenkins.Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=jenkins_server,
        )

        jenkins_job_parser.parse()

        columns = (
            'Region',
            'Application branch',
            'Stand url',
            'Configuration file UUID',
            'Job URL'
        )

        jobs_data = jenkins_job_parser.get_jobs_data_as_tuple(
            state=StandStateEnum.AVAILABLE,
        )

        rows = (
            (
                region,
                branch,
                url,
                configuration_file_uuid,
                job_url,
            )
            for region, branch, url, configuration_file_uuid, job_url in jobs_data  # noqa
        )

        return columns, rows


class BOJenkinsGenerateDatabaserInterfaceCommand(
    BOConfiguredToolCommand,
):
    """
    Команда для генерации Groovy скриптов для создания интерфейса Job-а в
    Jenkins
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Generating Jenkins Databaser interface Groovy scripts.'
        )

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOCONF_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--apply',
            dest='apply',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Apply generating Groovy code to Databaser Jenkins Job.'
            ),
        )

        return parser

    def _set_stand_activated_projects(
        self,
        stand_configuration: StandConfiguration,
    ):
        """
        Проставление активных проектов в конфигах тестовых стендов
        """
        configurations_path = Path(
            self._boconf_config.get(
                section='boconf',
                option='configurations_path',
            ).value
        )
        configurations_git_repository_url: str = self._boconf_config.get(
            section='boconf',
            option='configurations_git_repository_url',
        ).value

        bo_config_generator = BOConfigGenerator(
            stand_url=stand_configuration.url,
            projects_combination=ProjectEnum.get_projects(),
            configurations_path=configurations_path,
            configurations_git_repository_url=configurations_git_repository_url,
        )
        bo_config = bo_config_generator.generate()

        activated_plugins = map(
            lambda x: x.strip(),
            bo_config.get(
                section='plugins',
                option='activated_plugins',
            ).value.split(',')
        )

        activated_plugins = ProjectPluginEnum.get_enums_by_str_plugins(
            plugins=activated_plugins,
        )

        projects = ProjectPluginEnum.get_projects_by_plugins(
            plugins=activated_plugins,
        )

        stand_configuration.projects = sorted(projects)

    def _apply_parameters(
        self,
        generator: JenkinsGroovyScriptsGenerator,
        jenkins_server: Jenkins,
    ):
        """
        Применение сгенерированного кода в Jenkins Job
        """
        config = jenkins_server.get_job_config(
            self._bojenkins_config['jenkins']['databaser_job_name'].value
        )

        config = ET.canonicalize(xml_data=config, strip_text=True)

        root = ET.fromstring(config)

        parameters = root.find('properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions')

        for parameter in parameters.findall('org.biouno.unochoice.CascadeChoiceParameter'):
            parameter_name = parameter.find('name').text

            code = generator.get_code_by_parameter_name(
                parameter_name=parameter_name,
            )

            if code:
                script = parameter.find('script/secureScript/script')

                script.text = code

        prettified_xml = prettify_xml_element(root)

        jenkins_server.reconfig_job(
            name=self._bojenkins_config['jenkins']['databaser_job_name'].value,
            config_xml=prettified_xml,
        )

        logger.write(
            f"Jenkins Job configuration "
            f"{self._bojenkins_config['jenkins']['databaser_job_name'].value} "
            f"updated."
        )

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        jenkins_server = jenkins.Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=jenkins_server,
        )

        jenkins_job_parser.parse()

        stands_configurations = []

        jobs_data = jenkins_job_parser.get_jobs_data_as_tuple(
            state=StandStateEnum.AVAILABLE,
        )

        for _, branch, url, _, _ in jobs_data:
            stand_configuration = StandConfiguration(
                url=url,
                branch=branch,
            )

            try:
                self._set_stand_activated_projects(
                    stand_configuration=stand_configuration,
                )
            except (
                AppConfigUUIDCanNotGetFromServer,
                AppConfigUUIDNotFound,
            ) as e:
                logger.write(f'{e}\n')
            else:
                stands_configurations.append(
                    stand_configuration
                )

        generator = JenkinsGroovyScriptsGenerator(
            stands_configurations=stands_configurations,
        )
        generator.generate()

        if self._parsed_args.apply:
            self._apply_parameters(
                generator=generator,
                jenkins_server=jenkins_server,
            )


class BOJenkinsRunDatabaserCommand(
    BOConfiguredToolCommand,
):
    """
    Команда для запуска сборки Job-а Databaser в Jenkins
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            """Команда для запуска сборки среза БД при помощи Databaser посредством настроенного Job-а в Jenkins.
            
            При запуске команды производится проверка уже запущенных сборок Job-а. Если сборки существуют, то попытка 
            запуска сборки среза считается неудачной. Считаем, что пользовательские сборки имеют больший приоритет 
            перед теми, которые запускаются с использованием данной команды, в общем случае - автоматически по графику. 
            
            Если запущенных сборок нет, то производится поиск подходящей задачи в Jira, для которой необходимо получить 
            срез базы данных. Если номер задачи не был передан в параметре ``--issue_id``, то поиск производится по 
            фильтру, указанному в секции jenkins в параметре ``databaser_new_jira_filter``. 
            
            Если подходящая задача была найдена, то производится парсинг описания задачи, из которой выделяются такие 
            параметры, как URL тестового стенда и идентификаторы учреждений, данные которых должны находиться в срезе. 
            В описании, секция Параметры подключения к тестовому серверу имеет стандартизированный вид. 
            
            Если удалось распарсить URL тестового стенда и идентификаторы учреждений, производится запуск сборки Job-а 
            в Jenkins. В текущий момент реализована следующая логика работы:
            
            * Если в номере задачи указывается BOBUH, то в сборке будет только проект Бухгалтерия и Ядро;
            * Если в номере задачи указывается BOZIK, то в сборке будет только проект ЗиК и Ядро;
            * Если в номере задачи указывается BOAIP, то в сборке будет Бухгалтерия, Авто, Питание, Ядро.
            
            После того, как собраны все параметры, осуществляется запуск сборки среза БД. В задаче, для которой 
            осуществляется сборка, будет указан Адрес сборки среза и Статус сборки среза - Запущена.
            
            Мониторинг состояния запущенных таким образом сборок, осуществляется при помощи команды 
            ``bojenkin check databaser``.            
            """
        )

        self._jenkins_server = None
        self._jira_client = None

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOTELEGRAM_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
                BOJIRA_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--issue_id',
            dest='issue_id',
            action='store',
            default=None,
            type=lambda x: str(x).upper() if x else '',
            help=(
                'Номер задачи в Jira.'
            ),
        )

        parser.add_argument(
            '--issue_from_filter',
            dest='issue_from_filter',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Искать подходящую задачу согласно фильтра, указанного в настройках.'
            ),
        )

        parser.add_argument(
            '--notify',
            dest='notify',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Оповещать разработчиков о запущенной сборки среза БД в Jenkins и о возникающих ошибках.'
            ),
        )

        return parser

    def _get_required_projects(
        self,
        issue_id: str,
    ):
        project_name = issue_id.split('-')[0]

        return JIRA_PROJECTS_CONFORMITY[project_name]

    def _parse_jira_task_id_by_filter(
        self,
        jql_str: str,
    ):
        """
        Получение идентификатора задачи Jira из фильтра
        """
        issues = self._jira_client.search_issues(
            jql_str=jql_str,
            max_results=1,
        )

        issue = issues[0] if issues else None

        if issue:
            task_id = issue.key
        else:
            task_id = None

        return task_id

    def _get_jira_issue(
        self,
        task_id: str,
    ):
        """
        Получение задачи Jira
        """
        issue = self._jira_client.get_issue(
            issue_id=task_id,
        )

        return issue

    def _parse_stand_url_ent_ids(
        self,
        issue,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Получение URL тестового стенда и Идентификатора учреждения из описания
        задачи
        """
        parsing_stand_url_result = re.findall(
            JIRA_STAND_URL_RE,
            issue.fields.description,
        )

        stand_url = parsing_stand_url_result[0] if parsing_stand_url_result else None

        parsing_end_ids_result = re.findall(
            JIRA_ENT_IDS_RE,
            issue.fields.description,
        )

        ent_ids = ','.join(parsing_end_ids_result) if parsing_end_ids_result else None

        return stand_url, ent_ids

    def _parse_branch(
        self,
        stand_url: str,
    ) -> Optional[str]:
        """
        Получение ветки из описания Job-а
        """
        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=self._jenkins_server,
        )

        jenkins_job_parser.parse()

        job_data = jenkins_job_parser.get_job_data_by_stand_url(
            stand_url=stand_url,
        )

        if job_data:
            branch = job_data[1]
        else:
            branch = None

        return branch

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._jenkins_server = jenkins.Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        job_info = self._jenkins_server.get_job_info(
            name=self._bojenkins_config['jenkins']['databaser_job_name'].value,
        )

        if (
            not job_info['inQueue'] and
            job_info['lastBuild']['number'] == job_info['lastCompletedBuild']['number']  # noqa
        ):
            self._jira_client = JiraAPIClient(
                url=self._bojira_config['jira']['url'].value,
                username=self._bojira_config['jira']['username'].value,
                password=self._bojira_config['jira']['password'].value,
            )

            if self._parsed_args.issue_id:
                issue_id = self._parsed_args.issue_id
            else:
                if self._parsed_args.issue_from_filter:
                    issue_id = self._parse_jira_task_id_by_filter(
                        jql_str=self._bojenkins_config['jenkins']['databaser_new_jira_filter'].value,  # noqa
                    )
                else:
                    issue_id = None

            if issue_id:
                issue = self._get_jira_issue(
                    task_id=issue_id,
                )
                issue_url = prepare_jira_issue_url(
                    jira_url=self._bojira_config['jira']['url'].value,
                    issue_id=issue_id,
                )
                stand_url, ent_ids = self._parse_stand_url_ent_ids(
                    issue=issue,
                )

                if parsed_args.notify:
                    telegram_sender = TelegramMessageSender(
                        bot_api_token=self._botelegram_config['telegram']['bot_api_token'].value,
                        chat_ids=(
                            self._bojenkins_config['jenkins']['databaser_notification_telegram_chat_id'].value,
                        ),
                    )

                if stand_url and ent_ids:
                    branch = self._parse_branch(
                        stand_url=stand_url,
                    )

                    if branch:
                        required_projects = self._get_required_projects(
                            issue_id=issue_id,
                        )

                        parameters = {
                            'TAG': 'latest',
                            'TASK_ID': issue_id,
                            'ENT_IDS': ent_ids,
                            'STAND': stand_url,
                            'WEB_BB_APP_BRANCH': branch,
                            'WEB_BB_CORE_BRANCH': branch,
                            'WEB_BB_ACCOUNTING_BRANCH': (
                                branch if
                                ProjectEnum.WEB_BB_ACCOUNTING in required_projects else  # noqa
                                ''
                            ),
                            'WEB_BB_SALARY_BRANCH': (
                                branch if
                                ProjectEnum.WEB_BB_SALARY in required_projects else  # noqa
                                ''
                            ),
                            'WEB_BB_VEHICLE_BRANCH': (
                                branch if
                                ProjectEnum.WEB_BB_VEHICLE in required_projects else  # noqa
                                ''
                            ),
                            'WEB_BB_FOOD_BRANCH': (
                                branch if
                                ProjectEnum.WEB_BB_FOOD in required_projects else  # noqa
                                ''
                            ),
                            'EXCLUDED_TABLES': self._bojenkins_config['jenkins']['databaser_excluded_tables'].value,  # noqa
                        }

                        self._jenkins_server.build_job(
                            name=self._bojenkins_config['jenkins']['databaser_job_name'].value,  # noqa
                            parameters=parameters,
                        )

                        # Подождем, чтобы задача встала в очередь
                        time.sleep(45)

                        updated_job_info = self._jenkins_server.get_job_info(
                            name=self._bojenkins_config['jenkins']['databaser_job_name'].value,  # noqa
                        )
                        build_number = updated_job_info['lastBuild']['number']

                        self._jira_client.update_field(
                            issue=issue,
                            field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                            value=JiraBuildSlicingDBStatusEnum.RUNNING.value,
                        )

                        build_url = (
                            self._bojenkins_config['jenkins']['databaser_build_url_template'].value.format(  # noqa
                                jenkins_url=self._bojenkins_config['jenkins']['url'].value,  # noqa
                                jenkins_databaser_job_name=self._bojenkins_config['jenkins']['databaser_job_name'].value,  # noqa
                                build_number=build_number,
                            )
                        )

                        self._jira_client.update_field(
                            issue=issue,
                            field=JiraCustomFieldEnum.ADDRESS_BUILD_SLICING_DB.value,
                            value=quote(build_url, safe='/:'),
                        )

                        logger.write(
                            f'Databaser Job Build successful start with number '
                            f'{build_number} for issue {issue_url}.\n'
                        )

                        if parsed_args.notify:
                            telegram_sender.send(
                                message=(
                                    f'Для задачи {issue_url} была запущена сборка среза БД {quote(build_url, safe="/:")}'
                                ),
                            )
                    else:
                        self._jira_client.update_field(
                            issue=issue,
                            field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                            value=JiraBuildSlicingDBStatusEnum.STAND_UNAVAILABLE.value,
                        )

                        if parsed_args.notify:
                            telegram_sender.send(
                                message=(
                                    f'\U0001F640 Неудачная попытка запуска сборки среза БД для задачи {issue_url}. '
                                    f'Тестовый стенд {stand_url} недоступен!'
                                ),
                            )

                        raise RuntimeError(
                            f'Please check stand with URL {stand_url}, because '
                            f'now it is unavailable! Issue {issue_url}'
                        )
                else:
                    self._jira_client.update_field(
                        issue=issue,
                        field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                        value=JiraBuildSlicingDBStatusEnum.CAN_NOT_PARSE_STAND_URL_AND_ENT_ID.value,
                    )

                    if parsed_args.notify:
                        telegram_sender.send(
                            message=(
                                f'\U0001F640 Не удалось распарсить stand_url и ent_id из описания задачи в Jira. Необходимо '
                                f'проверить корректность описания и в случае необходимости внести исправления. Задача '
                                f'{issue_url}.'
                            ),
                        )

                    raise RuntimeError(
                        f'Can not parse stand_url and ent_id from Jira issue '
                        f'description. Please, check and rewrite description '
                        f'for start building Databaser Job. Issue {issue_url}'
                    )
            else:
                raise RuntimeError(
                    'Please set issue_id.'
                )
        else:
            raise RuntimeError(
                'Databaser Job Build already in the Queue or running now. Try '
                'to run command later.'
            )


class BOJenkinsCheckDatabaserCommand(
    DatabaserGeneralArgumentsMixin,
    BOConfiguredToolCommand,
):
    """
    Команда для проверки задач и сборок срезов БД для них. В рамках команды
    производится ряд действий:

    - Если сборка была запущена (databaser_build_running), то нужно проверить
        состояние сборки и изменить статус на:
        - databaser_build_finished, в случае удачной сборки;
        - databaser_build_finished_with_warnings, в случае удачной сборки с
            предупреждениями в логах билда;
        - databaser_build_broken, в случае неудачной сборки;
    - Если стенд был недоступен, проверить доступность;
    - Проверить последнюю сборку на время выполнения, если сборка ведется
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.description = (
            'Check Databaser builds.'
        )

        self._jenkins_server = None
        self._jira_client = None

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOTELEGRAM_TOOL_NAME,
                BOCONF_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
                BOJIRA_TOOL_NAME,
                BODATABASER_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--notify',
            dest='notify',
            action='store',
            default=False,
            type=lambda x: bool(strtobool(x)),
            help=(
                'Notify developers about running Jenkins builds and errors.'
            ),
        )

        return parser

    def _parse_jira_issues_by_filter(
        self,
        jql_str: str,
    ):
        """
        Получение идентификатора задачи Jira из фильтра
        """
        issues = self._jira_client.search_issues(
            jql_str=jql_str,
        )

        return issues

    def _check_build_console_errors(
        self,
        job_name: str,
        build_number: int,
    ):
        """
        Проверка наличия выброшенных исключений в логе
        """
        build_console_log = self._jenkins_server.get_build_console_output(
            name=job_name,
            number=build_number,
        )

        return 'Traceback' in build_console_log

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._jenkins_server = jenkins.Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        self._jira_client = JiraAPIClient(
            url=self._bojira_config['jira']['url'].value,
            username=self._bojira_config['jira']['username'].value,
            password=self._bojira_config['jira']['password'].value,
        )

        if parsed_args.notify:
            telegram_sender = TelegramMessageSender(
                bot_api_token=self._botelegram_config['telegram']['bot_api_token'].value,
                chat_ids=(
                    self._bojenkins_config['jenkins']['databaser_notification_telegram_chat_id'].value,
                ),
            )

        job_name = self._bojenkins_config['jenkins']['databaser_job_name'].value
        issues = self._parse_jira_issues_by_filter(
            jql_str=self._bojenkins_config['jenkins']['databaser_running_jira_filter'].value,
        )

        for issue in issues:
            issue_url = prepare_jira_issue_url(
                jira_url=self._bojira_config['jira']['url'].value,
                issue_id=issue.key,
            )
            databaser_build_url = getattr(issue.fields, JiraCustomFieldEnum.ADDRESS_BUILD_SLICING_DB.value)

            if databaser_build_url:

                build_number = int(databaser_build_url.split('/')[-2])

                build_info = self._jenkins_server.get_build_info(
                    name=job_name,
                    number=build_number,
                )

                if build_info['result'] == BuildResultEnum.SUCCESS.value:
                    with_errors = self._check_build_console_errors(
                        job_name=job_name,
                        build_number=build_number,
                    )

                    if with_errors:
                        self._jira_client.update_field(
                            issue=issue,
                            field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                            value=JiraBuildSlicingDBStatusEnum.FINISHED_WITH_WARNINGS.value,
                        )

                        logger.write(
                            f'Issue {issue_url} with build {databaser_build_url} success, but errors found!\n'
                        )

                        if parsed_args.notify:
                            telegram_sender.send(
                                message=(
                                    f'\U0001F640 Для задачи {issue_url} сборка среза БД {databaser_build_url} была завершена '
                                    f'успешно, но были выявлены ошибки!'
                                ),
                            )
                    else:
                        self._jira_client.update_field(
                            issue=issue,
                            field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                            value=JiraBuildSlicingDBStatusEnum.FINISHED.value,
                        )
                elif build_info['result'] == BuildResultEnum.FAILURE.value:
                    self._jira_client.update_field(
                        issue=issue,
                        field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                        value=JiraBuildSlicingDBStatusEnum.BROKEN.value,
                    )

                    logger.write(
                        f'Issue {issue_url} with build {databaser_build_url} failure!\n'
                    )

                    if parsed_args.notify:
                        telegram_sender.send(
                            message=(
                                f'\U0001F640 Для задачи {issue_url} сборка среза БД {databaser_build_url} завершилась '
                                f'с ошибками!'
                            ),
                        )
                elif build_info['result'] == BuildResultEnum.ABORTED.value:
                    self._jira_client.update_field(
                        issue=issue,
                        field=JiraCustomFieldEnum.STATUS_BUILD_SLICING_DB.value,
                        value=JiraBuildSlicingDBStatusEnum.ABORTED.value,
                    )

                    logger.write(
                        f'Issue {issue_url} with build {databaser_build_url} aborted!\n'
                    )

                    if parsed_args.notify:
                        telegram_sender.send(
                            message=(
                                f'\U0001F640 Для задачи {issue_url} сборка среза БД {databaser_build_url} была '
                                f'остановлена!'
                            ),
                        )
                elif build_info['result'] is None:
                    logger.write(
                        f'Issue {issue_url} with build {databaser_build_url} running now..\n'
                    )
                else:
                    logger.write(
                        f'Issue {issue_url} with build {databaser_build_url} found unidentified result status!\n'
                    )

                    if parsed_args.notify:
                        telegram_sender.send(
                            message=(
                                f'\U0001F640 Для задачи {issue_url} сборка среза БД {databaser_build_url} была '
                                f'завершена с неопознанным статусом!'
                            ),
                        )
            else:
                logger.write(
                    f'Issue {issue_url} without databaser build url error!\n'
                )

                if parsed_args.notify:
                    telegram_sender.send(
                        message=(
                            f'\U0001F640 В задаче {issue_url} не указан URL сборки среза БД!'
                        ),
                    )
