from django.views.generic.base import TemplateView

from .models import Story


class StoryView(TemplateView):
    template_name = "story/index.html"

    def get_context_data(self, **kwargs):
        return super(StoryView, self).get_context_data(
            story=Story.objects.get(pk=self.args[0]),
            **kwargs
        )
