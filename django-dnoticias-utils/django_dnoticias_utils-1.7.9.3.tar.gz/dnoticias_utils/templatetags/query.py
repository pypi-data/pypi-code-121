from django.utils.module_loading import import_string
from django.template import Library, Node
import logging

logger = logging.getLogger(__name__)

register = Library()

@register.simple_tag
def get_query(model_path, manager="_default_manager", *filter_args, **filter_kwargs):
    try:
        model = import_string(model_path)
        manager = getattr(model, manager ,model._default_manager)
        return manager.filter(*filter_args, **filter_kwargs)
    except Exception as e:
        logger.exception("Error in getting the query")
        return None
