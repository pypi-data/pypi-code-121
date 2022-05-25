import os

import pytest
from Crypto.PublicKey import RSA

import vessl
from test.conftest import USE_MOCK
from vessl.util.random import random_string


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestSshKey:
    @pytest.mark.order(index=1)
    def test_create_ssh_key(self):
        key_path = "test/fixture/pubkey"
        key = RSA.generate(1024).publickey()
        with open(key_path, "wb") as f:
            key_value = key.exportKey("OpenSSH")
            f.write(key_value)

        key_name = random_string()
        pytest.key = vessl.create_ssh_key(key_path, key_name, key_value.decode())
        os.remove(key_path)

    def test_list_ssh_keys(self):
        vessl.list_ssh_keys()

    def test_delete_ssh_key(self):
        vessl.delete_ssh_key(pytest.key.id)
