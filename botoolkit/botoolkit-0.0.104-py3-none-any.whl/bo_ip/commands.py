from argparse import (
    Namespace,
)
from pathlib import (
    Path,
)
from typing import (
    Dict,
)

from jenkins import (
    Jenkins,
)

from botoolkit.bo_conf.settings import (
    TOOL_NAME as BOCONF_TOOL_NAME,
)
from botoolkit.bo_ip.api import (
    IPAddressReachableChecker,
    StandIPAddressCollector,
)
from botoolkit.bo_ip.enums import (
    IPAddressStateEnum,
)
from botoolkit.bo_jenkins.parsers import (
    JenkinsJobParser,
)
from botoolkit.bo_jenkins.settings import (
    TOOL_NAME as BOJENKINS_TOOL_NAME,
)
from botoolkit.bo_toolkit.settings import (
    TOOL_NAME as BOTOOLKIT_TOOL_NAME,
)
from botoolkit.core.commands import (
    BOConfiguredToolLister,
)


class BOIPPingCommand(
    BOConfiguredToolLister,
):
    """
    Проверка доступности ip-адресов с хоста. Без указания параметров будет
    производиться проверка доступности серверов всех тестовых стендов и их баз
    данных
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
            """Команда для проверки доступности тестовых серверов и серверов с указанными в настройках тестовых стендов базами данных.
            
            При помощи команды можно оперативно узнать доступность серверов тестовых стендов для постановки задачи в 
            СТП для настройки роутинга.            
            """
        )

        self._ip_addresses = set()

    def get_required_config_tool_names(self):
        required_config_tool_names = super().get_required_config_tool_names()

        required_config_tool_names.extend(
            (
                BOTOOLKIT_TOOL_NAME,
                BOJENKINS_TOOL_NAME,
                BOCONF_TOOL_NAME,
            )
        )

        return required_config_tool_names

    def _collect_stands_ip_addresses(self):
        """
        Сбор ip-адресов из конфигурационных файлов тестовых стендов
        """
        jenkins_server = Jenkins(
            url=self._bojenkins_config['jenkins']['url'].value,
            username=self._bojenkins_config['jenkins']['username'].value,
            password=self._bojenkins_config['jenkins']['password'].value,
        )

        jenkins_job_parser = JenkinsJobParser(
            jenkins_server=jenkins_server,
        )

        jenkins_job_parser.parse()

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

        collector = StandIPAddressCollector(
            stands_urls=jenkins_job_parser.get_stand_urls(),
            ip_addresses_cache=self._ip_addresses,
            configurations_git_repository_url=configurations_git_repository_url,
            configurations_path=configurations_path,
        )

        collector.collect()

    def _collect_ip_addresses(self):
        """
        Сбор ip-адресов
        """
        if self._parsed_args.ip_address:
            self._ip_addresses.add(self._parsed_args.ip_address)
        else:
            self._collect_stands_ip_addresses()

    def _prepare_result(
        self,
        ip_addresses: Dict[str, IPAddressStateEnum]
    ):
        """
        Подготовка результата для вывода в виде таблицы
        """
        columns = (
            'IP Address',
            'State',
        )

        rows = (
            (
                ip_address,
                state.value,
            )
            for ip_address, state in ip_addresses.items()
        )

        return columns, rows

    def get_parser(
        self,
        prog_name,
    ):
        parser = super().get_parser(
            prog_name=prog_name,
        )

        parser.add_argument(
            '--ip_address',
            action='store',
            type=str,
        )

        return parser

    def take_action(
        self,
        parsed_args: Namespace,
    ):
        super().take_action(
            parsed_args=parsed_args,
        )

        self._collect_ip_addresses()

        reachable_checker = IPAddressReachableChecker(
            ip_addresses=self._ip_addresses,
        )
        checked_ip_addresses = reachable_checker.check()

        result = self._prepare_result(
            ip_addresses=checked_ip_addresses
        )

        return result
