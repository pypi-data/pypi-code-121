from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import Tuple
from uuid import UUID

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import NameAttribute, NameOID


def generate_self_signed_certificate(server_uuid: UUID, address: str) -> Tuple[bytes, bytes]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    issuer = subject = get_sila_consortium_x509_name()

    today = datetime.today()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(today - timedelta(hours=12))
        .not_valid_after(today + timedelta(days=364))
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH, x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_cert_sign=True,
                crl_sign=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
                content_commitment=False,
                data_encipherment=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(IPv4Address(address))]),
            critical=False,
        )
        .add_extension(
            x509.UnrecognizedExtension(x509.ObjectIdentifier("1.3.6.1.4.1.58583"), str(server_uuid).encode("ascii")),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)

    return private_key_bytes, cert_bytes


def get_sila_consortium_x509_name() -> x509.Name:
    return x509.Name(
        [
            NameAttribute(NameOID.COUNTRY_NAME, "CH"),  # Switzerland
            NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SG"),  # Canton of St. Gallen
            NameAttribute(NameOID.LOCALITY_NAME, "Rapperswil-Jona"),
            NameAttribute(NameOID.ORGANIZATION_NAME, "Association Consortium Standardization in Lab Automation (SiLA)"),
            NameAttribute(NameOID.COMMON_NAME, "SiLA2"),
        ]
    )
