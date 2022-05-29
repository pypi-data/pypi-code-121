from django.contrib import admin
from django.urls import path
from custom_url.views import CustomUrlView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<path:url>', CustomUrlView.as_view()),
]
