from django.template import Library, loader

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


register = Library()

# https://localcoder.org/django-inclusion-tag-with-configurable-template


@register.simple_tag(takes_context=True)
def make_counts(context):
    t = loader.get_template(f"counts/{context['theme']}.html")
    context.update({

    })
    logger.info(context)
    return t.render(context.flatten())


from django.template.defaultfilters import stringfilter


# 템플릿에서 문자열을 split하기 위해 커스텀 필터를 만듦
@register.filter
@stringfilter
def split(string, sep):
    """Return the string split by sep.

    Example usage: {{ value|split:"/" }}
    """
    return string.split(sep)
