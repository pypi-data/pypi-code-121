from django.test import TestCase, modify_settings

from custom_url.forms import CustomUrlForm

class CustomUrlFormTestCase(TestCase):
    
    def test_custom_url_form_invalid_url(self):
        """Testing invalid url in Custom URL form"""
        form = CustomUrlForm(data={
            'url':'/!hi/'
        })
        form.is_valid()
        self.assertIn('This value must be a valid URL path.', form.errors['url'])
    
    def test_custom_url_form_url_leading_slash(self):
        """Testing url's leading slash validation in Custom URL form""" 
        form = CustomUrlForm(data={
            'url':'hi/'
        })
        form.is_valid()
        self.assertIn('URL is missing a leading slash.', form.errors['url'])
    
    @modify_settings(
        MIDDLEWARE={'append': 'django.middleware.common.CommonMiddleware'}
    )
    def test_custom_url_form_url_trailing_slash_when_append_slash_true(self):
        """Testing url's trailing slash validation in Custom URL form when settings.APPEND_SLASH is True"""
        with self.settings(APPEND_SLASH=True):
            form = CustomUrlForm(data={
                'url':'/hi'
            })
            form.is_valid()
            self.assertIn('URL is missing a trailing slash.', form.errors['url'])