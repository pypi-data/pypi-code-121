from django.urls import path
from . import views

urlpatterns = [
    # A simple test page
    path("", views.index, name="authorize_index"),
    path("app/<str:app_code>/", views.app, name="authorize_app"),
    path("grant", views.grant, name="grant_permission"),
    path("revoke", views.revoke, name="revoke_permission_tbd"),
    path("revoke/<int:permission_id>/", views.revoke, name="revoke_permission"),
    # Manage Applications
    path("manage_applications", views.manage_apps, name="manage_applications"),
    path("new_applications", views.new_apps, name="new_applications"),
    # Manage Authorities
    path("manage_authorities", views.manage_authorities, name="manage_authorities"),
    path("new_authorities", views.new_authority, name="new_authorities"),
    path("delete_authority", views.delete_authority, name="delete_authority"),
    path(
        "delete_authority/<int:authority_id>/",
        views.delete_authority,
        name="delete_authorities",
    ),
]
