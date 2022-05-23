""" Base Django URL mapping for SatNOGS DB"""
from allauth import urls as allauth_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView

from db.api.urls import API_URLPATTERNS
from db.base.urls import BASE_URLPATTERNS

urlpatterns = [
    # Base
    path('', include(BASE_URLPATTERNS)),

    # Accounts
    path('accounts/', include(allauth_urls)),

    # API
    path('api/', include(API_URLPATTERNS)),

    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI view of our schema. Note the use of SpectacularSwaggerSplitView
    # is to avoid CSP issues without having to open up unsafe-inline.
    path('api/schema/docs/', SpectacularSwaggerSplitView.as_view(url_name='schema'), name='docs'),

    # Admin
    path('admin/', admin.site.urls),
]

# Auth0
if settings.AUTH0:
    urlpatterns += [
        path('', include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
        path('', include(('social_django.urls', 'social'), namespace='social'))
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
