from json.decoder import (
    JSONDecodeError,
)
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import requests
import validators
from jenkins import (
    Jenkins,
)
from requests import (
    Response,
)
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    ReadTimeout,
)
from simplejson.errors import (
    JSONDecodeError as SimpleJSONDecodeError,
)

from botoolkit.bo_git.enums import (
    BranchEnum,
)
from botoolkit.bo_ip.strings import (
    UNAVAILABLE,
)
from botoolkit.bo_jenkins.consts import (
    JENKINS_JOB_DISABLED_COLOR,
    JENKINS_JOB_RED_COLOR,
    JENKINS_VIEW_NAME,
)
from botoolkit.bo_jenkins.enums import (
    StandStateEnum,
)
from botoolkit.bo_jenkins.strings import (
    JENKINS_JOB_DESCRIPTION_PARSING_ERROR,
)
from botoolkit.core.loggers import (
    logger,
)


class JenkinsJobParser:
    """
    Парсер Job-ов тестовых стендов
    """

    def __init__(
        self,
        jenkins_server: Jenkins,
    ):
        self._jenkins_server = jenkins_server

        # Хранит данные Job-ов в виде словаря
        # {
        #   region: {
        #       branch: [
        #           {
        #               stand_url: ..,
        #               uuid: ..,
        #               job_url: ..,
        #           },
        #       ],
        #   },
        # }
        self._jobs_data: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

    def jobs_data_as_dict(
        self,
        state: StandStateEnum = StandStateEnum.ALL,
    ) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
        """
        Возвращает результат работы парсера Job-ов тестовых стендов в виде
        словаря
        """
        regions = self._jobs_data.keys()

        if state == StandStateEnum.AVAILABLE:
            regions = tuple(
                filter(
                    lambda r: r != UNAVAILABLE,
                    regions,
                )
            )
        elif state == StandStateEnum.UNAVAILABLE:
            regions = tuple(
                filter(
                    lambda r: r == UNAVAILABLE,
                    regions,
                )
            )

        filtered_jobs_data = {
            key: value
            for key, value in self._jobs_data.items() if
            key in regions
        }

        return filtered_jobs_data

    def get_jobs_data_as_tuple(
        self,
        state: StandStateEnum = StandStateEnum.ALL,
    ) -> List[Tuple[str, str, str, str, str]]:
        """
        Возвращает результат работы парсера Job-ов тестовых стендов в виде
        кортежа
        """
        records = []

        jobs_data = self.jobs_data_as_dict(
            state=state,
        )

        for region in jobs_data:
            for branch in jobs_data[region]:
                for job_data in jobs_data[region][branch]:
                    records.append(
                        (
                            region,
                            branch,
                            job_data['stand_url'],
                            job_data['configuration_file_uuid'],
                            job_data['job_url'],
                        )
                    )

        return records

    def get_job_data_by_stand_url(
        self,
        stand_url: str,
    ):
        """
        Возвращает данные Job-а найденного по URL тестового стенда
        """
        jobs_data = self.get_jobs_data_as_tuple(
            state=StandStateEnum.AVAILABLE,
        )

        try:
            job_data = next(filter(lambda x: x[2] == stand_url, jobs_data))
        except StopIteration:
            job_data = None

        return job_data

    @property
    def regions(self):
        return tuple(filter(lambda r: r != UNAVAILABLE, self._jobs_data.keys()))

    def get_stand_urls(
        self,
        state: StandStateEnum = StandStateEnum.ALL,
    ):
        """
        Получение адресов тестовых стендов в зависимости от указанного статуса
        """
        return [
            record[2]
            for record in self.get_jobs_data_as_tuple(
                state=state,
            )
        ]

    @property
    def major_region_stands(self) -> List[Tuple[str, str, str, str, str]]:
        """
        Возвращает данные тестовых стендов самых старших веток региона
        """
        records = []

        available_jobs_data = self.jobs_data_as_dict(
            state=StandStateEnum.AVAILABLE,
        )

        for region in available_jobs_data:
            branch = (
                BranchEnum.DEFAULT.value if
                BranchEnum.DEFAULT.value in self._jobs_data[region] else
                BranchEnum.TEST.value
            )

            jobs_data = self._jobs_data[region][branch]

            records.append(
                (
                    region,
                    branch,
                    jobs_data[0]['stand_url'],
                    jobs_data[0]['configuration_file_uuid'],
                    jobs_data[0]['job_url'],
                )
            )

        return records

    def _get_configuration_file_uuid(
        self,
        stand_url: str,
    ) -> Optional[str]:
        """
        Получение UUID конфигурационного файла
        """
        uuid = None
        config_uuid_url = f'{stand_url}config-uuid/'

        try:
            response: Response = requests.get(
                url=config_uuid_url,
                timeout=10,
            )

            if response.ok:
                try:
                    uuid = response.json()['app_config_uuid']
                except (
                    JSONDecodeError,
                    SimpleJSONDecodeError,
                ):
                    logger.write(
                        f'JSONDecodeError! Can not decode response from '
                        f'{config_uuid_url}\n'
                    )
        except (
            ConnectionError,
            ReadTimeout,
            ConnectTimeout,
        ):
            logger.write(
                f'Can not read configuration UUID by {config_uuid_url}. Stand '
                f'unavailable!\n'
            )

        return uuid

    def _get_region_abbreviation(
        self,
        stand_url: str,
    ) -> Optional[str]:
        """
        Возвращает аббревиатуру региона
        """
        region_abbreviation = None

        try:
            response: Response = requests.get(
                url=f'{stand_url}region-abbreviation/',
                timeout=10,
            )

            if response.ok:
                region_abbreviation = response.json()['app_region_abbreviation']
        except (
            ConnectionError,
            ReadTimeout,
        ):
            logger.write(f'Stand {stand_url} unavailable!')

        return region_abbreviation

    def _parse_jobs(self):
        jobs = self._jenkins_server.get_jobs(
            view_name=JENKINS_VIEW_NAME,
        )

        jobs = filter(
            lambda job: job.get('color') and job.get('color') not in [JENKINS_JOB_DISABLED_COLOR, JENKINS_JOB_RED_COLOR],  # noqa
            jobs
        )

        for job in jobs:
            job_info = self._jenkins_server.get_job_info(job.get('name'))

            job_description = (
                job_info['description'].strip() if
                job_info['description'] else
                ''
            )

            if 'http://' in job_description and 'ветка' in job_description:
                description_items = job_description.split(',')

                try:
                    stand_url = description_items[0].strip()

                    if '<a href' in stand_url:
                        stand_url = stand_url.split('href="')[1].split('">')[0]

                    branch = description_items[2].split('ветка ')[1]
                except IndexError:
                    raise RuntimeError(
                        JENKINS_JOB_DESCRIPTION_PARSING_ERROR.format(
                            job_name=job_info['displayName'],
                            job_description=job_description,
                        )
                    )

                if (
                    validators.url(stand_url) and
                    branch in BranchEnum.get_all_str()
                ):
                    configuration_file_uuid = self._get_configuration_file_uuid(
                        stand_url=stand_url,
                    )

                    if configuration_file_uuid:
                        region_abbreviation = self._get_region_abbreviation(
                            stand_url=stand_url,
                        )

                        if region_abbreviation not in self._jobs_data:
                            self._jobs_data[region_abbreviation] = {}

                        if branch not in self._jobs_data[region_abbreviation]:
                            self._jobs_data[region_abbreviation][branch] = []

                        self._jobs_data[region_abbreviation][branch].append(
                            {
                                'stand_url': stand_url,
                                'configuration_file_uuid': configuration_file_uuid,  # noqa
                                'job_url': job['url'],
                            }
                        )
                    else:
                        if UNAVAILABLE not in self._jobs_data:
                            self._jobs_data[UNAVAILABLE] = {}

                        if UNAVAILABLE not in self._jobs_data[UNAVAILABLE]:
                            self._jobs_data[UNAVAILABLE][branch] = []

                        self._jobs_data[UNAVAILABLE][branch].append(
                            {
                                'stand_url': stand_url,
                                'configuration_file_uuid': configuration_file_uuid,  # noqa
                                'job_url': job['url']
                            }
                        )

    def parse(self):
        self._parse_jobs()
