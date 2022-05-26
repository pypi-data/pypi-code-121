from datetime import datetime

from pydantic import Field
from pydantic.main import BaseModel

from edulib.models.base import Base, Page


class BaseOrmSchema(BaseModel):
    id: int = Field(
        ...,
        ge=1,
        title="Уникальный идентификатор",
        description="Для однозначного определения объекта",
    )
    created_at: datetime = Field(
        ..., title="Дата создания", description="Когда был создан объект"
    )
    updated_at: datetime = Field(
        ..., title="Дата обновления", description="Когда был обновлен объект"
    )
    is_active: bool = Field(
        ...,
        title="Активность",
        description=(
            "Переключатель активности объекта. Нужно ли его прятать или нет?"
        ),
    )

    class Config:
        orm_mode = True

    @classmethod
    def construct_from_orm(cls, orm_obj: Base) -> "BaseOrmSchema":
        values = {
            field_name: getattr(orm_obj, field_name)
            for field_name in cls.__fields__.keys()
        }
        return cls.construct(**values)


class BaseUpdateSchema(BaseModel):
    is_active: bool | None = Field(
        None,
        title="Активность",
        description=(
            "Переключатель активности объекта. Нужно ли его прятать или нет?"
        ),
        example=True,
    )


class BasePageSchema(BaseModel):
    total: int = Field(
        ...,
        ge=0,
        title="Всего",
        description=(
            "Количество объектов в базе, подходящих под заданные условия"
        ),
    )
    offset: int = Field(
        ...,
        ge=0,
        title="Отступ",
        description=(
            "Количество объектов в начале списка которые были пропущены"
        ),
    )
    limit: int | None = Field(
        None,
        ge=0,
        title="Лимит",
        description="Количество объектов которое запросили из базы",
    )
    items: list[BaseOrmSchema]

    @classmethod
    def construct_from_page(cls, page: Page) -> "BasePageSchema":
        schema: BaseOrmSchema = cls.__fields__["items"].type_
        items = [schema.construct_from_orm(item) for item in page.items]
        return cls.construct(
            total=page.total, offset=page.offset, limit=page.limit, items=items
        )
