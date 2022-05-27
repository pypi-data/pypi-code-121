from django.forms.widgets import Media, MediaDefiningClass
from django.test import TestCase

from altstreamfield.utils import get_class_media

class TestGetClassMedia(TestCase):

    def test_basic(self):
        class C1(metaclass=MediaDefiningClass):
            class Media:
                js = ['c1.js']
                css = {
                    'all': ['c1.css'],
                }

        class C2(C1):
            class Media:
                js = ['c2.js']

            @property
            def media(self):
                base = super().media
                return get_class_media(base, self)

        class C3(C1):
            class Media:
                js = ['c3.js']
                extend = ['css']

            @property
            def media(self):
                base = super().media
                return get_class_media(base, self)

        class C4(C1):
            class Media:
                js = ['c4.js']
                extend = False

            @property
            def media(self):
                base = super().media
                return get_class_media(base, self)

        inst = C2()
        self.assertIn('c1.js', inst.media._js)
        self.assertIn('c2.js', inst.media._js)
        self.assertIn('c1.css', inst.media._css['all'])

        inst = C3()
        self.assertIn('c3.js', inst.media._js)
        self.assertNotIn('c1.js', inst.media._js)
        self.assertIn('c1.css', inst.media._css['all'])

        inst = C4()
        self.assertIn('c4.js', inst.media._js)
        self.assertNotIn('c1.js', inst.media._js)
        self.assertNotIn('all', inst.media._css)

        class C5:
            pass

        base = Media()
        self.assertIs(get_class_media(base, C5()), base)