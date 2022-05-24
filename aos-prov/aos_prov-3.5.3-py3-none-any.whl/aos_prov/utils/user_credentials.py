#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#
import os
import tempfile
from os.path import isfile
from pathlib import Path
from typing import Optional

import OpenSSL
from colorama import Fore, Style
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives._serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates

from aos_prov.utils import SDK_SECURITY_PATH
from aos_prov.utils.errors import UserCredentialsError


def _extract_cloud_domain_from_cert(cert_bytes: bytes) -> str:
    """Get the Cloud domain name from user certificate."""
    private_key, certificate, additional_certificates = load_key_and_certificates(cert_bytes, None)
    return certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value


def _pkcs12_to_pem(pkcs12_bytes: bytes):
    private_key, certificate, additional_certificates = \
        load_key_and_certificates(pkcs12_bytes, ''.encode('utf8'), default_backend())

    cert_bytes = bytearray(certificate.public_bytes(Encoding.PEM))
    for add_cert in additional_certificates:
        cert_bytes += add_cert.public_bytes(Encoding.PEM)
    key_bytes = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    cert_bytes = bytes(cert_bytes)
    return cert_bytes, key_bytes


def _create_temp_file(data: bytes):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(data)
    tmp_file.close()
    return tmp_file.name


class TempCredentials:
    def __init__(self, certificate: Optional[bytes], key: Optional[bytes],
                 cert_file_name: Optional[str], key_file_name: Optional[str]):
        self._key_file_name = key_file_name
        self._cert_file_name = cert_file_name

        self._key = None
        self._certificate = None

        if certificate and key:
            self._key = key
            self._certificate = certificate

    def __enter__(self):
        if not self._key_file_name:
            self._key_file_name = _create_temp_file(self._key)
        if not self._cert_file_name:
            self._cert_file_name = _create_temp_file(self._certificate)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._key:
            os.unlink(self._key_file_name)
            self._key_file_name = None
        if self._certificate:
            os.unlink(self._cert_file_name)
            self._cert_file_name = None

    @property
    def key_file_name(self):
        return self._key_file_name

    @property
    def cert_file_name(self):
        return self._cert_file_name


class UserCredentials:

    def __init__(self, cert_file_path: Optional[str], key_file_path: Optional[str], pkcs12: Optional[str]):
        self._cert_file_path = cert_file_path
        self._key_file_path = key_file_path
        self._cloud_url = None
        if pkcs12:
            if Path(pkcs12).exists():
                with open(pkcs12, 'rb') as pkcs12_file:
                    pkcs12_file_content = pkcs12_file.read()
                    cert_bytes, key_bytes = _pkcs12_to_pem(pkcs12_file_content)
                    self._user_credentials = TempCredentials(certificate=cert_bytes, key=key_bytes,
                                                             cert_file_name=None, key_file_name=None)
                    self._cloud_url = _extract_cloud_domain_from_cert(pkcs12_file_content)
            else:
                if not Path(cert_file_path).exists() or not Path(key_file_path).exists():
                    raise UserCredentialsError(f'User credentials file f{pkcs12} not found.')
                else:
                    self._user_credentials = TempCredentials(cert_file_name=cert_file_path, key_file_name=key_file_path,
                                                             certificate=None, key=None)
                    self._validate_credentials_format()
                    self._cloud_url = self._extract_cloud_url()

        else:
            if not Path(cert_file_path).exists():
                raise UserCredentialsError(f'User credentials file f{cert_file_path} not found.')
            elif not Path(key_file_path).exists():
                raise UserCredentialsError(f'User credentials file f{key_file_path} not found.')
            else:
                self._user_credentials = TempCredentials(cert_file_name=cert_file_path, key_file_name=key_file_path,
                                                         certificate=None, key=None)
                self._validate_credentials_format()
                self._cloud_url = self._extract_cloud_url()

    @property
    def cloud_url(self):
        return self._cloud_url

    @property
    def user_credentials(self):
        return self._user_credentials

    def _check_credentials_access(self):
        """ Validate existence and access to user credential files

            Raises:
                UserCredentialsError: If credentials files are not found
            Returns:
                None
        """

        # if not isfile(self._cert_file_path):

        if not isfile(self._cert_file_path):
            text = (f"{Fore.RED}Can't find user certificate file...{Style.RESET_ALL}\n\n"
                    f"Copy file to the default directory: [{SDK_SECURITY_PATH}] \n"
                    f"or set path to the certificate file with argument: --cert \n"
                    f"(Example: aos-prov -u 127.0.0.1 --cert /path/to/certfile) \n")
            raise UserCredentialsError(text)

        if not isfile(self._key_file_path):
            text = (f"{Fore.RED}Can't find user key file...{Style.RESET_ALL}\n\n"
                    f"Copy file to the default directory: [{SDK_SECURITY_PATH}] \n"
                    f"or set path to the key file with argument: --key \n"
                    f"(Example: aos-prov -u 127.0.0.1 --key /path/to/keyfile) \n")
            raise UserCredentialsError(text)

    def _validate_credentials_format(self):
        """ Validate format of user credential files

            Raises:
                UserCredentialsError: If credentials files are in wrong format or with errors
            Returns:
                None
        """
        with open(self._cert_file_path, "rb") as c, open(self._key_file_path, "r") as k:
            cert_content = c.read()
            key_content = k.read()

        try:
            private_key_obj = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, key_content)
        except OpenSSL.crypto.Error:
            raise UserCredentialsError('private key is not correct')

        try:
            cert_obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_content)
        except OpenSSL.crypto.Error:
            raise UserCredentialsError('Certificate is not correct: %s' % key_content)

        context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_2_METHOD)
        context.use_privatekey(private_key_obj)
        context.use_certificate(cert_obj)
        try:
            context.check_privatekey()
        except OpenSSL.SSL.Error:
            raise UserCredentialsError('User private key does not match certificate')

    def _extract_cloud_url(self):
        """Get the Cloud domain name from user certificate"""
        with open(self._cert_file_path, "rb") as cert:
            return OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM,
                cert.read()
            ).get_subject().organizationName
