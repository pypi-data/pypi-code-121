from django.urls import path, re_path, include

from .views import JavaScriptCatalogView


app_name = 'vuejs_translate'

urlpatterns = [
     path('i18n.js', JavaScriptCatalogView.as_view(), name='js-i18n'),
     path('i18n.<str:hash>.js', JavaScriptCatalogView.as_view(), name='js-i18n'),
]
