import hashlib

# md5加密
def md5_encryption(content: str):
    md5 = hashlib.md5()
    md5.update(content.encode('utf-8'))
    return md5.hexdigest()

# md5 校验
def md5_verify(content: str, md5_content: str):
    md5 = hashlib.md5()
    md5.update(content.encode('utf-8'))
    return md5.hexdigest() == md5_content