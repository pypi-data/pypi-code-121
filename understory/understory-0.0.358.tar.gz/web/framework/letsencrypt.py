"""A simple Let's Encrypt interface (via `acme-tiny`)."""

import pathlib
import subprocess

import acme_tiny


def generate_cert(domain, cert_dir):
    """Generate a TLS certificate signed by Let's Encrypt for given domain."""
    cert_dir = pathlib.Path(cert_dir)
    account_key = cert_dir / "account.key"
    if not account_key.exists():
        with account_key.open("w") as fp:
            subprocess.call(["openssl", "genrsa", "4096"], stdout=fp)
    private_key = cert_dir / "domain.key"
    if not private_key.exists():
        with private_key.open("w") as fp:
            subprocess.call(["openssl", "genrsa", "4096"], stdout=fp)
    csr = cert_dir / "domain.csr"
    if not csr.exists():
        with csr.open("w") as fp:
            subprocess.call(
                [
                    "openssl",
                    "req",
                    "-new",
                    "-sha256",
                    "-key",
                    private_key,
                    "-subj",
                    f"/CN={domain}",
                ],
                stdout=fp,
            )
    with (cert_dir / "domain.crt").open("w") as fp:
        fp.write(acme_tiny.get_crt(account_key, csr, cert_dir / "challenges"))
    csr.unlink()
