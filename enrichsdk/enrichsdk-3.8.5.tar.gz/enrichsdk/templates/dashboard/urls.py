from django.conf.urls import url, include
from . import views, catalog, custom
from dashboard.app import *

app_name = "APPNAME"

# => Base
urlpatterns = []

# Custom app
customspec = custom.get_spec()
register_app_instance(
    appmod="enrichapp.dashboard.custom",
    namespace="default",
    rootnamespace=app_name,
    urlpatterns=urlpatterns,
    spec=customspec,
    app_urlpatterns=[
        url('^[/]?$', views.index, name="index"),
    ]
)

catalogspec = catalog.get_spec()
register_app_instance(
    appmod="enrichapp.dashboard.catalog",
    namespace="catalog",
    rootnamespace=app_name,
    urlpatterns=urlpatterns,
    spec=catalogspec)

#from . import persona
#searchspec = persona.get_spec()
#register_app_instance(
#    appmod="enrichapp.dashboard.persona",
#    namespace="persona",
#    rootnamespace=app_name,
#    urlpatterns=urlpatterns,
#    spec=searchspec)
#
