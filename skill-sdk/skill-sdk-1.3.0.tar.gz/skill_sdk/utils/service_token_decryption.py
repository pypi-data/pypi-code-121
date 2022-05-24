#
# voice-skill-sdk
#
# (C) 2022, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#


import base64
import json
import logging

from skill_sdk.intents import r
from skill_sdk.config import settings
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)


class ServiceTokenDecryption:
    """
    Utility class responsible for decrypting the cv service-token.

    NOTE :: Please do not store the user related token claims
            in any permanent persistence storage due to GDR compliance issues.
            Currently there is not any existing mechanism for cleaning up any user related data.
    """

    CVI_SERVICE_TOKEN_NAME = "cvi"

    @classmethod
    def decrypt(cls):
        """
        Verifies and decrypts the cvi service-token.
        Returns the claims of the token

        :return:
            the claims of the token

        :Raises ValueError:
            if the MAC does not match. The message has been tampered with
            or the key is incorrect.
        """
        service_token: str = r.context.tokens[cls.CVI_SERVICE_TOKEN_NAME]
        service_token_secret: str = settings.CVI_SERVICE_TOKEN_SECRET

        decoded_cvi_token: bytes = base64.b64decode(service_token)
        decoded_str = str(decoded_cvi_token, "utf-8")
        decoded_dict: dict = json.loads(decoded_str)
        decoded_nonce = base64.b64decode(decoded_dict.get("nonce"))
        decoded_encrypted_plain_token = base64.b64decode(
            decoded_dict.get("encryptedPlainToken")
        )
        decoded_secret: bytes = base64.b64decode(service_token_secret)

        cipher = AES.new(decoded_secret, AES.MODE_GCM, decoded_nonce)  # Setup cipher
        # Raw data structure for encryptedPlainToken crypttext[:-16] + auth_tag[-16:] aka default cipher.block_size
        decoded_cipher_text = decoded_encrypted_plain_token[: -cipher.block_size]
        decoded_auth_tag = decoded_encrypted_plain_token[-cipher.block_size :]
        try:
            plaintext = cipher.decrypt_and_verify(
                decoded_cipher_text,
                decoded_auth_tag,
            )
            logger.debug(str(plaintext, "utf-8"))
        except ValueError as e:
            logger.error(e)
            raise e
        token_data = json.loads(str(plaintext, "utf-8"))
        return token_data
