from django.urls import path

from .views import (
    admin,
    create_requests,
    effective_requests,
    manage_requests,
    standings,
)

app_name = "standingsrequests"

urlpatterns = [
    # index
    path("", create_requests.index_view, name="index"),
    # admin
    path(
        "admin_changeset_update_now/",
        admin.admin_changeset_update_now,
        name="admin_changeset_update_now",
    ),
    # create_requests
    path("create_requests", create_requests.create_requests, name="create_requests"),
    path(
        "request_characters",
        create_requests.request_characters,
        name="request_characters",
    ),
    path(
        "request_corporations",
        create_requests.request_corporations,
        name="request_corporations",
    ),
    path(
        "request_character_standing/<int:character_id>/",
        create_requests.request_character_standing,
        name="request_character_standing",
    ),
    path(
        "remove_character_standing/<int:character_id>/",
        create_requests.remove_character_standing,
        name="remove_character_standing",
    ),
    path(
        "request_corp_standing/<int:corporation_id>/",
        create_requests.request_corp_standing,
        name="request_corp_standing",
    ),
    path(
        "remove_corp_standing/<int:corporation_id>/",
        create_requests.remove_corp_standing,
        name="remove_corp_standing",
    ),
    path("manage/setuptoken/", create_requests.view_auth_page, name="view_auth_page"),
    path(
        "requester_add_scopes/",
        create_requests.view_requester_add_scopes,
        name="view_requester_add_scopes",
    ),
    # effective requests
    path(
        "view/requests/",
        effective_requests.effective_requests,
        name="effective_requests",
    ),
    path(
        "view/requests/data/",
        effective_requests.effective_requests_data,
        name="effective_requests_data",
    ),
    # manage requests
    path("manage/", manage_requests.manage_standings, name="manage"),
    path(
        "manage/requests/",
        manage_requests.manage_requests_list,
        name="manage_requests_list",
    ),  # Should always follow the path of the GET path above
    path(
        "manage/requests/<int:contact_id>/",
        manage_requests.manage_requests_write,
        name="manage_requests_write",
    ),
    path(
        "manage/revocations/",
        manage_requests.manage_revocations_list,
        name="manage_revocations_list",
    ),
    path(
        "manage/revocations/<int:contact_id>/",
        manage_requests.manage_revocations_write,
        name="manage_revocations_write",
    ),
    # Standings
    path("standings", standings.standings, name="standings"),
    path(
        "standings/characters/data",
        standings.character_standings_data,
        name="character_standings_data",
    ),
    path(
        "standings/characters/download",
        standings.download_pilot_standings,
        name="download_pilots",
    ),
    path(
        "standings/corporations/data",
        standings.corporation_standings_data,
        name="corporation_standings_data",
    ),
    path(
        "standings/alliances/data",
        standings.alliance_standings_data,
        name="alliance_standings_data",
    ),
]
