import base64

from Cryptodome.Hash import SHA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Cryptodome.PublicKey import RSA


# 生成密钥对
def generate_rsa_key(secret: str='', bits: int=4096, pcks: int=8, protection: str='scryptAndAES128-CBC') -> tuple():
    rsa = RSA.generate(bits)
    server_private_pem = rsa.exportKey(passphrase=secret, pkcs=pcks, protection=protection)
    server_public_pem = rsa.publickey().exportKey(passphrase=secret, pkcs=pcks, protection=protection)
    client_private_pem = rsa.exportKey(passphrase=secret, pkcs=pcks, protection=protection)
    client_public_pem = rsa.publickey().exportKey(passphrase=secret, pkcs=pcks, protection=protection)
    return server_private_pem, server_public_pem, client_private_pem, client_public_pem


# rsa加密
def rsa_encrypt(client_public_pem: bytes, content: bytes, secret: str='') -> bytes:
    rsakey = RSA.importKey(client_public_pem, passphrase=secret)
    cipher = PKCS1_OAEP.new(rsakey)
    return base64.b64encode(cipher.encrypt(content))


# rsa签名
def rsa_sign(server_private_pem: bytes, content: bytes, secret: str='') -> bytes:
    rsakey = RSA.importKey(server_private_pem, passphrase=secret)
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(content)
    sign = signer.sign(digest)
    return base64.b64encode(sign)  # 签名


# rsa解密
def rsa_decrypt(client_private_pem: str, encrypt_content: str, secret: str=''):
    rsakey = RSA.importKey(client_private_pem, passphrase=secret)
    cipher = PKCS1_OAEP.new(rsakey)
    return cipher.decrypt(base64.b64decode(encrypt_content.encode('utf-8'))).decode('utf-8')  # 加密后的内容


# rsa验签
def rsa_verify(server_public_pem: str, decrypt_content: str, sign_content: str, secret: str=''):
    rsakey = RSA.importKey(server_public_pem, passphrase=secret)
    verifier = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA.new()
    digest.update(decrypt_content.encode('utf-8'))
    return verifier.verify(digest, base64.b64decode(sign_content.encode('utf-8')))