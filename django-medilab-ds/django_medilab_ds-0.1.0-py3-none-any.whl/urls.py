from django.urls import path, include
from . import views

app_name = 'medilab_ds'

urlpatterns = [
    path('', views.buildup, name='buildup'),
    path('portfolio/', include('portfolio.urls')),
]