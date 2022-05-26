from django.conf.urls import url

from .views import MatrixInviterView

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/matrix_inviter/$",
        MatrixInviterView.as_view(),
        name="settings",
    )
]
