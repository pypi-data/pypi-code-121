import re
import hmac
import hashlib


class WebhookMixin:
    """
    Mixin for working with webhooks
    """

    HEADER_REGEX = r"^t=(\d+),s=(\w+)$"

    def verify_webhook(self, request_body, signature_header, webhook_secret):
        """
        Verify webhook request

        :param request_body: Raw request body of webhook as bytes
        :type request_body: bytes
        :param signature_header: Signature header of request. Mercury signature header
            is Mercury-Signature
        :type signature_header: str
        :param webhook_secret: Secret configured in Mercury for the user
        :type webhook_secret: str
        :return: Boolean of whether the webhook request is valid
        :rtype: bool
        """

        timestamp, signature = self._extract_timestamp_signature(signature_header)

        digest_message = "{}.{}".format(timestamp, request_body.decode("utf-8"))
        generated_signature = self._generate_signature(webhook_secret, digest_message)
        return hmac.compare_digest(signature, generated_signature)

    def _generate_signature(self, webhook_secret, digest_message):
        """
        generate_signature Generate signature from secret and message

        :param webhook_secret: Key for the digest
        :type webhook_secret: str
        :param digest_message: Message fto be digested
        :type digest_message: str
        :return: Generated signature
        :rtype: str
        """
        return hmac.new(
            webhook_secret.encode("utf-8"),
            digest_message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _extract_timestamp_signature(self, signature_header):
        """
        Get timestamp and signature from Mercury-Signature header

        :param signature_header: Value of Mercury-Signature header form webhook
        :type signature_header: str
        :return: Tuple containing timestamp and signature
        :rtype: (str, str)
        """
        m = re.match(self.HEADER_REGEX, signature_header)
        if m is None:
            raise ValueError("Signature header is invalid")

        timestamp = m.group(1)
        signature = m.group(2)
        return timestamp, signature
