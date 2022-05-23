from django.test import TestCase


class ModelfilterTestCase(TestCase):
    modelfilter_css_file = 'modelfilter.css'
    modelfilter_js_file = 'modelfilter.js'

    def test_css_exists(self):
        response = self.client.get('/admin/', follow=True)
        self.assertContains(response, self.modelfilter_css_file)

    def test_js_exists(self):
        response = self.client.get('/admin/', follow=True)
        self.assertContains(response, self.modelfilter_js_file)
