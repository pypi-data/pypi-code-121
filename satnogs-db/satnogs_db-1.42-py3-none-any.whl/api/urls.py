"""SatNOGS DB django rest framework API url routings"""
from django.urls import include, path
from rest_framework import routers

from db.api import views

ROUTER = routers.DefaultRouter()

ROUTER.register(r'artifacts', views.ArtifactViewSet)
ROUTER.register(r'modes', views.ModeViewSet)
ROUTER.register(r'satellites', views.SatelliteViewSet)
ROUTER.register(r'transmitters', views.TransmitterViewSet)
ROUTER.register(r'telemetry', views.TelemetryViewSet)
ROUTER.register(r'tle', views.LatestTleSetViewSet)

API_URLPATTERNS = [
    # Keep combatibility by allowing to get satellite object with NORAD
    # ID.Adding 'basename' value to use it in custom renderers.
    path(
        'satellites/<int:satellite_entry__norad_cat_id>/',
        views.SatelliteViewSet.as_view({'get': 'retrieve'}, basename='latestsatellite')
    ),
    path('', include(ROUTER.urls))
]
