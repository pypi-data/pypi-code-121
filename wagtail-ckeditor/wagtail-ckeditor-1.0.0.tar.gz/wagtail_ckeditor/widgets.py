from __future__ import absolute_import, unicode_literals

from django.forms import Media, widgets
from django.templatetags.static import static
from wagtail.utils.widgets import WidgetWithScript


class CKEditor(WidgetWithScript, widgets.Textarea):
    def render_js_init(self, id_, name, value):
        return f"initCKEditor({id_})"

    @property
    def media(self):
        return Media(
            js=[
                static("wagtail_ckeditor/ckeditor.js"),
                static("wagtail_ckeditor/initEditor.js"),
            ]
        )
