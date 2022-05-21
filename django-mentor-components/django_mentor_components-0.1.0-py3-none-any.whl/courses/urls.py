from django.urls import path
from . import views

app_name = 'courses_details'

urlpatterns = [
    path('<int:id>/', views.details, name='details'),
]
