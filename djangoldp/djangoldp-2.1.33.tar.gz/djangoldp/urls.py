from importlib import import_module

from django.conf import settings
from django.conf.urls import re_path, include

from djangoldp.models import LDPSource, Model
from djangoldp.permissions import LDPPermissions
from djangoldp.views import LDPSourceViewSet, WebFingerView, InboxView
from djangoldp.views import LDPViewSet


def __clean_path(path):
    '''ensures path is Django-friendly'''
    if path.startswith("/"):
        path = path[1:]
    if not path.endswith("/"):
        path = "{}/".format(path)
    return path


def get_all_non_abstract_subclasses(cls):
    '''
    returns a set of all subclasses for a given Python class (recursively calls cls.__subclasses__()). Ignores Abstract
    classes
    '''
    def valid_subclass(sc):
        '''returns True if the parameterised subclass is valid and should be returned'''
        return not Model.get_meta(sc, 'abstract', False)

    return set(c for c in cls.__subclasses__() if valid_subclass(c)).union(
        [s for c in cls.__subclasses__() for s in get_all_non_abstract_subclasses(c) if valid_subclass(s)])


def get_all_non_abstract_subclasses_dict(cls):
    '''returns a dict of class name -> class for all subclasses of given cls parameter (recursively)'''
    return {cls.__name__: cls for cls in get_all_non_abstract_subclasses(cls)}


urlpatterns = [
    re_path(r'^sources/(?P<federation>\w+)/', LDPSourceViewSet.urls(model=LDPSource, fields=['federation', 'urlid'],
                                                                    permission_classes=[LDPPermissions], )),
    re_path(r'^\.well-known/webfinger/?$', WebFingerView.as_view()),
    re_path(r'^inbox/$', InboxView.as_view()),
]

for package in settings.DJANGOLDP_PACKAGES:
    try:
        import_module('{}.models'.format(package))
    except ModuleNotFoundError:
        pass
    try:
        urlpatterns.append(re_path(r'^', include('{}.djangoldp_urls'.format(package))))
    except ModuleNotFoundError:
        pass

# fetch a list of all models which subclass DjangoLDP Model
model_classes = get_all_non_abstract_subclasses_dict(Model)

# append urls for all DjangoLDP Model subclasses
for class_name in model_classes:
    model_class = model_classes[class_name]
    # the path is the url for this model
    path = __clean_path(model_class.get_container_path())
    # urls_fct will be a method which generates urls for a ViewSet (defined in LDPViewSetGenerator)
    urls_fct = model_class.get_view_set().urls
    urlpatterns.append(re_path(r'^' + path,
        urls_fct(model=model_class,
                 lookup_field=Model.get_meta(model_class, 'lookup_field', 'pk'),
                 permission_classes=Model.get_meta(model_class, 'permission_classes', [LDPPermissions]),
                 fields=Model.get_meta(model_class, 'serializer_fields', []),
                 nested_fields=model_class.nested.fields())))

# NOTE: this route will be ignored if a custom (subclass of Model) user model is used, or it is registered by a package
# Django matches the first url it finds for a given path
urlpatterns.append(re_path(r'^users/', LDPViewSet.urls(model=settings.AUTH_USER_MODEL, permission_classes=[])))
