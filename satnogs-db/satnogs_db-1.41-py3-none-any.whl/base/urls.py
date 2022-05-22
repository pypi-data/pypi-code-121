"""Django base URL routings for SatNOGS DB"""
from django.urls import path, re_path

from db.base import views

BASE_URLPATTERNS = (
    [
        path('', views.home, name='home'),
        path('about/', views.about, name='about'),
        path('satellites/', views.satellites, name='satellites'),
        re_path(
            r'^satellite/(?P<sat_id>[A-Z]{4,4}(?:-\d\d\d\d){4,4})/$',
            views.satellite,
            name='satellite'
        ),
        path('satellite/<int:norad>/', views.satellite, name='satellite'),
        path(
            'satellite_suggestion_handler/',
            views.satellite_suggestion_handler,
            name='satellite_suggestion_handler'
        ),
        path('frames/<int:sat_pk>/', views.request_export, name='request_export_all'),
        path('frames/<int:sat_pk>/<int:period>/', views.request_export, name='request_export'),
        path('help/', views.satnogs_help, name='help'),
        path(
            'transmitter_suggestion_handler/',
            views.transmitter_suggestion_handler,
            name='transmitter_suggestion_handler'
        ),
        path('transmitters/', views.transmitters_list, name='transmitters_list'),
        path('statistics/', views.statistics, name='statistics'),
        path('stats/', views.stats, name='stats'),
        path('users/edit/', views.users_edit, name='users_edit'),
        path('robots.txt', views.robots, name='robots'),
        path('search/', views.search, name='search_results'),
        path('merge_satellites/', views.MergeSatellitesView.as_view(), name='merge_satellites'),
        path('create_satellite/', views.SatelliteCreateView.as_view(), name='create_satellite'),
        path(
            'update_satellite/<int:pk>/',
            views.SatelliteUpdateView.as_view(),
            name='update_satellite'
        ),
        path(
            'create_transmitter/<int:satellite_pk>',
            views.TransmitterCreateView.as_view(),
            name='create_transmitter'
        ),
        path(
            'update_transmitter/<int:pk>',
            views.TransmitterUpdateView.as_view(),
            name='update_transmitter'
        ),
        path(
            'ajax/recent_decoded_cnt/<int:norad>',
            views.recent_decoded_cnt,
            name='recent_decoded_cnt'
        ),
    ]
)
