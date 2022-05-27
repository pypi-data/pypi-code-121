from .views import DirtyHackAuthCheckViewSet, auth_view

from django.urls import path, include
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'check', DirtyHackAuthCheckViewSet, basename='xauth_check')

urlpatterns = [
	path('auth-post', auth_view),
	path('', include(router.urls)),
]
