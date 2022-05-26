from typing import Type, Union

from django.db.models import Model
from django.urls import reverse


def detail_url_for_model(model: Model, primary_key: Union[str, int, None] = None):
    used_primary_key: Union[str, int] = primary_key if primary_key else model.pk
    return detail_url_for_model_class(model.__class__, used_primary_key)


def detail_url_for_model_class(model: Type[Model], primary_key: Union[str, int]):
    view_name = _base_name_from_model_class(model) + "-detail"

    url = reverse(
        viewname=view_name,
        kwargs={"pk": primary_key},
    )
    return url


def list_url_for_model_class(model_class: Type[Model]):
    return reverse(_base_name_from_model_class(model_class) + "-list")


def list_url_for_model(model: Model):
    return list_url_for_model_class(model.__class__)


def _base_name_from_model_class(model_class: Type[Model]) -> str:
    return model_class.__name__.lower()


def base_name_from_model(model: Model) -> str:
    return _base_name_from_model_class(model.__class__)


__all__ = [
    "detail_url_for_model",
    "detail_url_for_model_class",
    "list_url_for_model_class",
    "list_url_for_model",
    "base_name_from_model",
]
