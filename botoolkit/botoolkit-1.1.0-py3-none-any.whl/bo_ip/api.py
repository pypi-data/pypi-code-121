from pathlib import (
    Path,
)
from socket import (
    gethostbyname,
)
from typing import (
    Dict,
    Iterable,
    Set,
)
from urllib.parse import (
    urlparse,
)

from requests.exceptions import (
    ConnectionError,
)
from validators import (
    ipv4,
)

from botoolkit.bo_conf.api import (
    BOConfigGenerator,
)
from botoolkit.bo_ip.enums import (
    IPAddressStateEnum,
)
from botoolkit.bo_ip.helpers import (
    ping_ip_address,
)
from botoolkit.bo_web_bb.exceptions import (
    AppConfigUUIDCanNotGetFromServer,
    AppConfigUUIDNotFound,
)
from botoolkit.core.loggers import (
    logger,
)


class IPAddressReachableChecker:
    """
    Класс для проверки доступности
    """

    def __init__(
        self,
        ip_addresses: Iterable[str],
    ):
        self._ip_addresses = {
            ip_address: IPAddressStateEnum.NOT_CHECKED
            for ip_address in ip_addresses
        }

    def _validate(self):
        """
        Валидация ip-адресов
        """
        for ip_address in self._ip_addresses.keys():
            self._ip_addresses[ip_address] = (
                IPAddressStateEnum.VALID if
                ipv4(ip_address) else
                IPAddressStateEnum.INVALID
            )

    def _ping(self):
        """
        Проверка доступности
        """
        for ip_address, state in self._ip_addresses.items():
            if state == IPAddressStateEnum.VALID:
                self._ip_addresses[ip_address] = ping_ip_address(
                    ip_address=ip_address,
                )

    def check(self) -> Dict[str, IPAddressStateEnum]:
        """
        Запуск проверки ip-адресов на доступность с хостовой машины
        """
        self._validate()
        self._ping()

        return self._ip_addresses


class StandIPAddressCollector:
    """
    Сборщик ip-адресов тестового стенда
    """

    def __init__(
        self,
        stands_urls: Iterable[str],
        ip_addresses_cache: Set[str],
        configurations_git_repository_url: str,
        configurations_path: Path,
    ):
        self._stands_urls = stands_urls
        self._ip_addresses_cache = ip_addresses_cache

        self._configurations_git_repository_url = configurations_git_repository_url
        self._configurations_path = configurations_path

    def _parse_host_name(
        self,
        hostname: str,
    ) -> str:
        """
        Парсинг имени хоста
        """
        if ipv4(hostname):
            ip_address = hostname
        else:
            try:
                ip_address = gethostbyname(hostname)
            except Exception as e:
                ip_address = None

        return ip_address

    def _parse_stand_ip_address(
        self,
        stand_url: str,
    ) -> str:
        """
        Получение ip-адреса из URL тестового стенда
        """
        parse_result = urlparse(stand_url)

        ip_address = self._parse_host_name(
            hostname=parse_result.hostname,
        )

        if ip_address:
            self._ip_addresses_cache.add(ip_address)

        return ip_address

    def _parse_stand_ip_addresses_from_config(
        self,
        stand_url: str,
    ):
        """
        Получение ip-адресов из конфигурационного файла тестового стенда
        """
        bo_config_generator = BOConfigGenerator(
            stand_url=stand_url,
            projects_combination=(),
            configurations_path=self._configurations_path,
            configurations_git_repository_url=(
                self._configurations_git_repository_url
            ),
        )

        try:
            web_bb_config = bo_config_generator.generate()

            database_host_ip = self._parse_host_name(
                hostname=web_bb_config['database']['database_host'].value
            )

            if database_host_ip:    
                self._ip_addresses_cache.add(database_host_ip)
        except AppConfigUUIDCanNotGetFromServer as e:
            logger.write(f'{e}\n')

    def _parse_stand_ip_addresses(
        self,
        stand_url: str,
    ):
        ip_address = self._parse_stand_ip_address(
            stand_url=stand_url,
        )

        if ip_address:
            checker = IPAddressReachableChecker(
                ip_addresses=(
                    ip_address,
                ),
            )
            checked_ip_addresses = checker.check()

            if checked_ip_addresses[ip_address] == IPAddressStateEnum.REACHABLE:
                self._parse_stand_ip_addresses_from_config(
                    stand_url=stand_url,
                )

    def collect(self):
        for stand_url in self._stands_urls:
            try:
                self._parse_stand_ip_addresses(
                    stand_url=stand_url,
                )
            except (
                AppConfigUUIDNotFound,
                ConnectionError,
            )as e:
                logger.write(f'{e}\n')
