from tempfile import TemporaryDirectory
from pathlib import Path
from zut.process import call

def download_public_key(keyid: str, target_path: Path, keyserver: str = None):
    with TemporaryDirectory() as tmpdir:
        # Retrieve the key
        cmd = ["gpg", "--homedir", tmpdir]
        if keyserver:
            cmd += ["--keyserver", keyserver]
        cmd += ["--recv-keys", keyid]
        call(cmd, accept_stderr=True)

        # Export the key
        cmd = ["gpg", "--homedir", tmpdir, "--output", target_path, "--export", keyid]
        call(cmd)

def verify(sign_path: Path, public_key_path: Path):
    call(["gpg", "--no-default-keyring", "--keyring", public_key_path, "--verify", sign_path], accept_stderr=True)
