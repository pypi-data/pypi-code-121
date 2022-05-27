from django.urls import re_path

from unicef_security.views import UnauthorizedView, UNICEFLogoutView

urlpatterns = [
    re_path(r'^unicef-logout/', UNICEFLogoutView.as_view(), name='unicef-logout'),
    re_path(r'^unauthorized/$', UnauthorizedView.as_view(), name="unauthorized"),
]
