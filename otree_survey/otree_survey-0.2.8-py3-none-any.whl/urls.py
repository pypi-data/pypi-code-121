import os

from django.conf import settings
from django.urls import path, re_path
from django.views.generic.base import RedirectView, TemplateView
from otree.urls import urlpatterns as otree_urlpatterns

from otree_survey.pages import About
from otree_survey.participant.views import JoinSessionAnonymouslyWithParams

custom_urlpatterns = []

# custom join session
View = JoinSessionAnonymouslyWithParams
custom_urlpatterns.append(re_path(View.url_pattern, View.as_view()))

# about page
about_url = getattr(settings, "ABOUT_URL", "about/")
custom_urlpatterns.append(path(about_url, About.as_view()))

# redirect / to about page for non-demo deployments
if (
    getattr(settings, "INDEX_TO_ABOUT", False)
    and os.environ.get("OTREE_AUTH_LEVEL", "DEMO") != "DEMO"
):
    custom_urlpatterns.append(re_path(r"^$", RedirectView.as_view(url=f"/{about_url}")))

# exclude robots
if getattr(settings, "EXCLUDE_ROBOTS", False):
    custom_urlpatterns.append(
        path(
            "robots.txt",
            TemplateView.as_view(
                template_name="otree_survey/robots.txt", content_type="text/plain"
            ),
        )
    )

# --- the rest requires setting this module as settings.ROOT_URLCONF ---

# use the above and the ortee default urls
urlpatterns = custom_urlpatterns + otree_urlpatterns

# custom errors
handler404 = "otree_survey.errors.views.handler404"
handler500 = "otree_survey.errors.views.handler500"
handler403 = "otree_survey.errors.views.handler403"
handler400 = "otree_survey.errors.views.handler400"
