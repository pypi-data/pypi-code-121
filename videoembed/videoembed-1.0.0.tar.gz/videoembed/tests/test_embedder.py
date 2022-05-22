from unittest import TestCase

from videoembed import Embedder
from videoembed.exceptions import ProviderNotFound
from videoembed.providers.vimeo import VimeoProvider
from videoembed.providers.youtube import YoutubeProvider


class TestEmbedder(TestCase):

    embedder: Embedder

    def setUp(self):
        self.embedder = Embedder()

    def test___init___config(self):
        config = {
            'width': 500,
            'height': 500,
            'autoplay': True
        }

        # do it
        embedder = Embedder(**config)

        # condition
        self.assertIsInstance(embedder.config, dict)
        self.assertEqual(embedder.config, config)

    def test___init___no_config(self):
        # do it
        embedder = Embedder()

        # condition
        self.assertIsInstance(embedder.config, dict)
        self.assertEqual(embedder.config, {})

    def test___call___raises_ProviderNotFound(self):
        video_url = 'invalid-provider-url.com'

        # condition
        with self.assertRaises(ProviderNotFound):
            self.embedder(video_url)

    def test___call___returns_YoutubeProvider(self):
        video_url = 'https://www.youtube.com/watch?v=_YUugB4IUl4'

        # do it
        provider = self.embedder(video_url)

        # condition
        self.assertIsInstance(provider, YoutubeProvider)

    def test___call___returns_VimeoProvider(self):
        video_url = 'https://vimeo.com/52355782'

        # do it
        provider = self.embedder(video_url)

        # condition
        self.assertIsInstance(provider, VimeoProvider)

    def test__get_provider__raises_ProviderNotFound(self):
        config = {}
        video_url = 'invalid-provider-url.com'

        # condition
        with self.assertRaises(ProviderNotFound):
            self.embedder._get_provider(video_url, config)

    def test__get_provider__returns_YoutubeProvider(self):
        config = {}
        video_url = 'https://www.youtube.com/watch?v=_YUugB4IUl4'

        # do it
        provider = self.embedder._get_provider(video_url, config)

        # condition
        self.assertIsInstance(provider, YoutubeProvider)

    def test__get_provider__returns_VimeoProvider(self):
        config = {}
        video_url = 'https://vimeo.com/52355782'

        # do it
        provider = self.embedder._get_provider(video_url, config)

        # condition
        self.assertIsInstance(provider, VimeoProvider)
