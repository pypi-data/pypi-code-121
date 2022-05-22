
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from tecdoc import views


app_name = 'tecdoc'


urlpatterns = [
    path('search/', views.find_article, name='search')
]

app_urls = i18n_patterns(
    path('tecdoc/', include((urlpatterns, app_name)))
)
