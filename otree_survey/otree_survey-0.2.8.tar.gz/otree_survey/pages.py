from django.views.generic import TemplateView
from otree.common import get_app_label_from_import_path


class AutoTemplateView(TemplateView):
    """Automatically generates template path (borrowed from otree.api.Page)"""

    def get_template_names(self):
        if self.template_name is not None:
            return [self.template_name]
        return [
            "{}/{}.html".format(
                get_app_label_from_import_path(self.__module__), self.__class__.__name__
            )
        ]


class About(AutoTemplateView):
    pass
