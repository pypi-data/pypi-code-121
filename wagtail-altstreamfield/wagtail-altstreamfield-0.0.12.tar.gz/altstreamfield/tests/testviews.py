from django.test import TestCase
from django.urls import reverse
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailTestUtils

class TestChooserPageData(TestCase, WagtailTestUtils):

    def test_basic(self):
        '''Ensures that this works when there is a matching page.'''
        page = Page.objects.get(id=2)

        self.login()
        response = self.client.get(reverse('wagtailadmin_choose_page_data', args=[page.id]))
        data = response.json()
        self.assertEqual(data['result']['id'], 2)
        self.assertEqual(data['step'], 'page_chosen')

