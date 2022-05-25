from unittest import TestCase

from mercuryclient.api import MercuryApi


class WebhookMixinTest(TestCase):
    def test_extract_signature_timestamp(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        sample_header = "t=677548800,s=3c0098c1f95739fc8167fb1bb05d014066d8381fc6a50a03ab665a57e239042a"
        ts, sign = client._extract_timestamp_signature(sample_header)

        self.assertEqual(ts, "677548800")
        self.assertEqual(
            sign, "3c0098c1f95739fc8167fb1bb05d014066d8381fc6a50a03ab665a57e239042a"
        )

    def test_verify_webhook(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )

        sample_header = "t=677548800,s=3c0098c1f95739fc8167fb1bb05d014066d8381fc6a50a03ab665a57e239042a"
        sample_body = b'{"sample_key": "sample_value"}'
        sample_secret = "SAMPLE_KEY"

        self.assertTrue(
            client.verify_webhook(sample_body, sample_header, sample_secret)
        )

        sample_secret = "INCORRECT_KEY"
        self.assertFalse(
            client.verify_webhook(sample_body, sample_header, sample_secret)
        )
