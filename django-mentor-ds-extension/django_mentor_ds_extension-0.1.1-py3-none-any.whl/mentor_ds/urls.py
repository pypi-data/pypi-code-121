from django.urls import path, include
from . import views

app_name = 'mentor_ds'

urlpatterns = [
    path('', views.buildup, name='buildup'),
    path('<str:lang>/', views.buildup, name='buildup'),
    path('courses/', include('courses.urls')),
]