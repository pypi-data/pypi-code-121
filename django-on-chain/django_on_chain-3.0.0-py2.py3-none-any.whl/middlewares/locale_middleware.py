from django.utils import translation

try:
    from django.utils.deprecation import MiddlewareMixin as base_class
except ImportError:  # For django 1.8.14
    base_class = object


class LocaleMiddleware(base_class):
    @staticmethod
    def process_request(request):
        lang = request.GET.get('lang', 'en')
        translation.activate(lang)
