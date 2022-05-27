import json
from robertcommonbasic.basic.encrypt.rsa import *

def test_rsa():
    secret = 'robert'
    content = json.dumps({'name': 'hello', 'value': 'world'})
    server_private_pem, server_public_pem, client_private_pem, client_public_pem = generate_rsa_key(secret)
    encrypt_content = rsa_encrypt(client_public_pem, content.encode('utf-8'), secret)
    sign_content = rsa_sign(server_private_pem, content.encode('utf-8'), secret)
    decrypt_content = rsa_decrypt(client_private_pem, encrypt_content.decode('utf-8'), secret)
    assert rsa_verify(server_public_pem, encrypt_content.decode('utf-8'), sign_content.decode('utf-8'), secret) == True

test_rsa()