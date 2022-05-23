from django.conf.urls import patterns, url

from .views import StoryView


urlpatterns = patterns(
    '',
    url(r'^(\d+)/', StoryView.as_view()),
)
