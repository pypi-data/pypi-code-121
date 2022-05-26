from typing import Any, Dict, Union

from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from dropland.storages.sql.model import UpdateSchemaType


# noinspection PyUnresolvedReferences
class ApiModelMixin:
    @classmethod
    async def get_or_404(cls, id_value: Any, **kwargs) -> 'Model':
        res = await cls.get(id_value, **kwargs)
        if not res:
            raise HTTPException(HTTP_404_NOT_FOUND, 'Not found')
        return res

    @classmethod
    async def update_or_404(cls, id_value: Any, data: Union[UpdateSchemaType, Dict[str, Any]]) -> 'Model':
        res = await cls.update_by_id(id_value, data)
        if not res:
            raise HTTPException(HTTP_404_NOT_FOUND, 'Not found')
        return res

    @classmethod
    async def delete_or_404(cls, id_value: Any) -> bool:
        res = await cls.delete_by_id(id_value)
        if not res:
            raise HTTPException(HTTP_404_NOT_FOUND, 'Not found')
        return res
