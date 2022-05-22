from typing import (
    Tuple,
    Union,
)

import psycopg2

from botoolkit.bo_postgres.enums import (
    DBImageTypeEnum,
)
from botoolkit.bo_web_bb.enums import (
    ProjectEnum,
)


def get_parent_projects_combination(
    src_combination: Tuple[ProjectEnum],
):
    """
    Получение родительской комбинации проектов
    """
    parent_combination = None
    combination_size = len(src_combination) - 1

    if src_combination and combination_size:
        allowed_combinations_weights = []

        filtered_combinations = filter(
            lambda c: len(c) == combination_size,
            ProjectEnum.get_projects_combinations()
        )

        for combination in filtered_combinations:
            is_include = all(p in src_combination for p in combination)

            if is_include:
                allowed_combinations_weights.append(
                    (
                        combination,
                        ProjectEnum.get_projects_combination_weight(
                            projects_combination=combination,
                        )
                    )
                )

        if allowed_combinations_weights:
            sorted_allowed_combinations_weight = sorted(
                allowed_combinations_weights,
                key=lambda combination_weight: combination_weight[1],
                reverse=True,
            )

            parent_combination = sorted_allowed_combinations_weight[0][0]

    return parent_combination


def generate_db_image_name(
    projects_combination: Tuple[ProjectEnum],
    type_: DBImageTypeEnum,
    region: str = None,
    tag: str = 'latest',
    split_tag: bool = False
) -> Union[str, Tuple[str, str]]:
    """
    Генерация имени образа БД
    """
    parts = [
        type_.value,
    ]

    if region:
        parts.append(region)

    parts.extend(
        list(map(lambda p: p.short(), sorted(projects_combination)))
    )

    image_name = f"{'-'.join(parts)}"

    if split_tag:
        result = image_name, tag
    else:
        result = f'{image_name}:{tag}'

    return result


class DBQueryExecutor:
    """
    Добавляет возможность выполнять запросы к указанной БД
    """

    def __init__(
        self,
        database: str,
        user: str,
        password: str,
        host: str,
        port: str,
    ):
        self._database = database
        self._user = user
        self._password = password
        self._host = host
        self._port = int(port)

        self._connection = None
        self._cursor = None

    def open(self):
        """
        Открытие соединения
        """
        is_open = False

        try:
            self._connection = psycopg2.connect(
                database=self._database,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port,
            )

            self._cursor = self._connection.cursor()

            is_open = True
        except psycopg2.OperationalError:
            self.close()

        return is_open

    def close(self):
        """
        Закрытие соединения
        """
        if self._cursor:
            self._cursor.close()

        if self._connection:
            self._connection.close()

    def execute(
        self,
        raw_sql: str,
    ):
        """
        Выполнение запроса
        """
        self._cursor.execute(raw_sql)

    def fetchone(
        self,
        raw_sql,
    ):
        """
        Выполняет запрос и возвращает одну строку
        """
        self.execute(
            raw_sql=raw_sql,
        )

        return self._cursor.fetchone()