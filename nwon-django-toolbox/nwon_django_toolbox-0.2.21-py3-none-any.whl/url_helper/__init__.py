from nwon_django_toolbox.url_helper.admin_url import (
    django_admin_link_for_model,
    formatted_django_admin_link,
)
from nwon_django_toolbox.url_helper.url_helper import (
    detail_url_for_model,
    detail_url_for_model_class,
    list_url_for_model,
    list_url_for_model_class,
)

__all__ = [
    "detail_url_for_model",
    "detail_url_for_model_class",
    "list_url_for_model_class",
    "list_url_for_model",
    "formatted_django_admin_link",
    "django_admin_link_for_model",
]
