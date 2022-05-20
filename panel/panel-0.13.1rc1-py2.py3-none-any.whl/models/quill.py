from bokeh.core.properties import Any, Bool, Enum, Either, List, String
from bokeh.models import HTMLBox

from ..io.resources import bundled_files
from ..util import classproperty


class QuillInput(HTMLBox):
    """
    WYSIWYG text editor based on Quill.js
    """

    __css_raw__ = [
        'https://cdn.quilljs.com/1.3.6/quill.bubble.css',
        'https://cdn.quilljs.com/1.3.6/quill.snow.css'
    ]

    __javascript_raw__ = [
        'https://cdn.quilljs.com/1.3.6/quill.js',
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    @classproperty
    def __js_skip__(cls):
        return {'Quill': cls.__javascript__}

    __js_require__ = {
        'paths': {
            'Quill': 'https://cdn.quilljs.com/1.3.6/quill',
        },
        'exports': {
            'Quill': 'Quill'
        }
    }

    mode = Enum("bubble", "toolbar", default='toolbar')

    placeholder = String()

    text = String()

    toolbar = Either(List(Any), Bool)
