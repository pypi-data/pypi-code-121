from django.conf import settings
from django.views.generic import RedirectView, TemplateView

from unicef_security.config import UNICEF_EMAIL


class UnauthorizedView(TemplateView):
    template_name = 'unauthorized.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unicef_user'] = self.request.user.is_authenticated and self.request.user.email.endswith(UNICEF_EMAIL)
        return context


class UNICEFLogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return f'https://{settings.TENANT_B2C_URL}/{settings.TENANT_ID}/{settings.POLICY}/oauth2/v2.0/' \
               f'logout?post_logout_redirect_uri={settings.HOST}{settings.LOGOUT_URL}'
