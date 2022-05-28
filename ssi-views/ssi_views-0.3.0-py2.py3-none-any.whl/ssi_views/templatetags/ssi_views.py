from django.template import Library
from django.utils.html import format_html

from ..logging import logger
from ..registry import registry

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

try:
    import jinja2
except ImportError:
    jinja2 = None


register = Library()


@register.simple_tag(name='ssi_url')
def do_ssi_url(name):
    if name not in registry:
        logger.warning('view `%s` is not registered' % name)
    return reverse('ssi_views:router', kwargs={'name': name})


@register.simple_tag(name='ssi_include')
def do_ssi_include(name):
    if name not in registry:
        logger.warning('view `%s` is not registered' % name)
    url = reverse('ssi_views:router', kwargs={'name': name})
    return format_html('<!--# include virtual="{}" -->', url)


if jinja2 is not None:
    from jinja2 import nodes
    from jinja2.ext import Extension

    class SSIIncludeExtension(Extension):
        tags = {'ssi_include'}

        def parse(self, parser):
            lineno = next(parser.stream).lineno
            view_name = parser.parse_expression()
            call = self.call_method('_ssi_include', [view_name])
            return nodes.Output([call], lineno=lineno)

        @staticmethod
        def _ssi_include(view_name):
            return do_ssi_include(view_name)

    # django-jinja support
    try:
        from django_jinja import library
    except ImportError:
        pass
    else:
        library.global_function(name='ssi_url')(do_ssi_url)
        library.extension(SSIIncludeExtension)
