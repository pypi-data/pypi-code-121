#redis返回的是byte类型的数据，转成字符串
def decode_byte_dict(byte_dict):
    str_dict = {}
    for bkey, bvalue in byte_dict.items():
        str_dict[bkey.decode()] = str(bvalue.decode())
    return str_dict
