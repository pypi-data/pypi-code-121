from django.contrib import admin
from django.urls import re_path
from example.views import poi_list

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', poi_list),
    re_path(r'^admin/', admin.site.urls),
]
