

from re_common.vip.baseencodeid import BaseLngid


def encode_id():
    """"
    由 sub_db_id 和 rawid 得到 lngid。
    case_insensitive: 标识源网站的 rawid 是否区分大小写
    """

    sub_db_id = "1"
    rawid = "AaaA123"
    b = BaseLngid()
    print("********区分大小写************")
    lngid = b.GetLngid(sub_db_id,
                       rawid,
                       case_insensitive=True)
    print(lngid)
    print("********不区分大小写************")
    lngid = b.GetLngid(sub_db_id,
                       rawid,
                       case_insensitive=False)
    print(lngid)

def decode_id():
    """
    limited_id 是由 lngid去除sub_db_id后得到的字符串
    limited_id超过20长度时，为不可逆的
    :return:
    """
    limited_id_big = "HKP4T9FSHL16LD1Q"
    limited_id_small = "HKP5N9G8JH09Y"
    limited_id_err = "123456" * 20
    b = BaseLngid()
    print("********区分大小写************")
    rawid = b.GetRawid(limited_id_big,
                       case_insensitive=True)
    print(rawid)
    print("********不区分大小写************")
    rawid = b.GetRawid(limited_id_small,
                       case_insensitive=False)
    print(rawid)
    print("*******limited_id超过20长度时*******")
    rawid = b.GetRawid(limited_id_err,
                       case_insensitive=False)





if __name__ == '__main__':
    encode_id()
    # decode_id()