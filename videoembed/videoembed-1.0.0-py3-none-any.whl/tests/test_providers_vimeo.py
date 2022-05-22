from unittest import TestCase

from videoembed.exceptions import APIRequestFailed
from videoembed.providers.base import TRequestParams, TThumbnailData
from videoembed.providers.vimeo import VimeoProvider, TOembedVimeoData


class TestVimeoProvider(TestCase):

    config: dict
    video_id: str
    video_url: str
    provider: VimeoProvider

    def setUp(self):
        self.config = {}
        self.video_id = '52355782'
        self.video_url = f'https://vimeo.com/{self.video_id}'
        self.provider = VimeoProvider(self.video_url, self.config)

    def test___init___default_config(self):
        # do it
        provider = VimeoProvider(self.video_url, self.config)

        # condition
        self.assertEqual(provider.video_url, self.video_url)
        self.assertEqual(provider.width, 640)
        self.assertEqual(provider.height, 360)
        self.assertEqual(provider.autoplay, False)

    def test___init___custom_config(self):
        # do it
        config = {
            'width': 1000,
            'height': 1000,
            'autoplay': True,
            'extra': 'super extra'
        }
        provider = VimeoProvider(self.video_url, config)

        # conditions
        self.assertEqual(provider.width, config['width'])
        self.assertEqual(provider.height, config['height'])
        self.assertEqual(provider.autoplay, config['autoplay'])
        self.assertFalse(hasattr(provider, 'extra'))

    def test__build_request_params(self):
        # do it
        request_params = self.provider._build_request_params()

        # condition
        self.assertIsInstance(request_params, dict)
        self.assertEqual(request_params.keys(), set(TRequestParams.__annotations__.keys()))
        self.assertEqual(request_params['maxwidth'], self.provider.width)
        self.assertEqual(request_params['maxheight'], self.provider.height)
        self.assertEqual(request_params['autoplay'], self.provider.autoplay)
        self.assertEqual(request_params['url'], self.provider.video_url)
        self.assertEqual(request_params['format'], 'json')

    def test_make_request__success(self):
        # do it
        result = self.provider.make_request()

        # condition
        self.assertIsInstance(result, dict)
        self.assertEqual(result.keys(), set(TOembedVimeoData.__annotations__.keys()))

    def test_make_request__raises_APIRequestFailed(self):
        # setup
        self.provider.video_url = 'invalid-video-url.com'

        # condition
        with self.assertRaises(APIRequestFailed):
            self.provider.make_request()

    def test_thumbnail_property(self):
        # do it
        thumbnail_data = self.provider.thumbnail

        # condition
        self.assertIsInstance(thumbnail_data, dict)
        self.assertEqual(thumbnail_data.keys(), set(TThumbnailData.__annotations__.keys()))

    def test_embed_code_property__autoplay_false(self):
        # do it
        embed_code = self.provider.embed_code

        # condition
        self.assertIsInstance(embed_code, str)
        self.assertNotIn('autoplay=1', embed_code)
        self.assertTrue(embed_code.startswith('<iframe '))
        self.assertTrue(embed_code.endswith('</iframe>'))
        self.assertIn(self.video_id, embed_code)
        self.assertIn('src="', embed_code)
        # we are only testing height, because width is auto adjusted to keep the ratio
        self.assertIn(f'height="{self.provider.height}"', embed_code)

    def test_embed_code_property__autoplay_true(self):
        # setup
        config = {
            'autoplay': True
        }
        provider = VimeoProvider(self.video_url, config)

        # do it
        embed_code = provider.embed_code

        # condition
        self.assertIsInstance(embed_code, str)
        self.assertIn('autoplay=1', embed_code)
        self.assertTrue(embed_code.startswith('<iframe '))
        self.assertTrue(embed_code.endswith('</iframe>'))
        self.assertIn(self.video_id, embed_code)
        self.assertIn('src="', embed_code)
        # we are only testing height, because width is auto adjusted to keep the ratio
        self.assertIn(f'height="{self.provider.height}"', embed_code)
