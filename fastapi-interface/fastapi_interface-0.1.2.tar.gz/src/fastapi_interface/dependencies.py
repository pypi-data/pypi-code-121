from fastapi import Query, Path

from fastapi_interface.constants import DEFAULT_OFFSET, DEFAULT_LIMIT


# TODO попробуй dataclass
class PaginationQueryParams:
    def __init__(
        self,
        offset: int = Query(
            DEFAULT_OFFSET,
            ge=0,
            title="Отступ",
            description="Для пагинации. Сколько объектов пропустить с начала?",
        ),
        limit: int
        | None = Query(
            DEFAULT_LIMIT,
            ge=0,
            title="Лимит",
            description="Для пагинации. Сколько объектов выбрать?",
        ),
    ):
        self.offset = offset
        self.limit = limit


def get_id_query_param(
    id_: int
    | None = Query(
        None,
        alias="id",
        ge=1,
        title="Уникальный идентификатор",
        description="Объект с каким id выбрать?",
    )
):
    return id_


def get_id_path_param(id_: int = Path(..., alias="id", ge=1)):
    return id_
