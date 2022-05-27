from __future__ import absolute_import, unicode_literals

from django.forms import Media, widgets
from wagtail.utils.widgets import WidgetWithScript

from .settings import config


class CKEditor(WidgetWithScript, widgets.Textarea):
    def render_js_init(self, id_, name, value):
        return (
            "ClassicEditor.create"
            "(document.getElementById('{id}', {config}))".format(
                id=id_, config=config
            )
        )

    @property
    def media(self):
        return Media(js=["wagtail_ckeditor/ckeditor.js"])
