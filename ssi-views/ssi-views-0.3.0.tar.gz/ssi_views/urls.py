import django

from .registry import registry
from .views import router

if django.VERSION >= (2, 2):  # noqa
    from django.urls import ResolverMatch, URLPattern
    from django.urls.resolvers import RegexPattern

    class SSIURLPattern(URLPattern):
        def resolve(self, path):
            match = self.pattern.match(path)
            if match:
                new_path, args, kwargs = match
                name = kwargs.pop('name')
                if name not in registry:
                    return
                view = registry[name]
                return ResolverMatch(
                    view, args, kwargs, self.pattern.name, route=str(self.pattern)
                )

    def ssi_url(regex, view, kwargs=None, name=None):
        pattern = RegexPattern(regex, name=name, is_endpoint=True)
        return SSIURLPattern(pattern, view, kwargs, name)


elif django.VERSION >= (2, 0):
    from django.urls import ResolverMatch, URLPattern
    from django.urls.resolvers import RegexPattern

    class SSIURLPattern(URLPattern):  # type: ignore
        def resolve(self, path):
            match = self.pattern.match(path)
            if match:
                new_path, args, kwargs = match
                name = kwargs.pop('name')
                if name not in registry:
                    return
                view = registry[name]
                return ResolverMatch(view, args, kwargs, self.pattern.name)

    def ssi_url(regex, view, kwargs=None, name=None):
        pattern = RegexPattern(regex, name=name, is_endpoint=True)
        return SSIURLPattern(pattern, view, kwargs, name)


else:
    from django.core.urlresolvers import RegexURLPattern, ResolverMatch

    class SSIURLPattern(RegexURLPattern):  # type: ignore
        def resolve(self, path):
            match = self.regex.search(path)
            if match:
                kwargs = match.groupdict()
                name = kwargs.pop('name')
                if name not in registry:
                    return
                view = registry[name]
                return ResolverMatch(view, (), kwargs, self.name)

    def ssi_url(regex, view, kwargs=None, name=None):
        return SSIURLPattern(regex, view, kwargs, name)


app_name = 'ssi_views'
urlpatterns = [
    ssi_url(r'(?P<name>[-\w.]+)/', router, name='router'),
]
