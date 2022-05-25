from pysmx.SM2 import generate_keypair as sm2_generate_keypair, Sign as sm2_Sign, Verify as sm2_Verify, \
    Encrypt as sm2_Encrypt, Decrypt as sm2_Decrypt
from pysmx.SM3 import SM3
from pysmx.SM4 import Sm4, ENCRYPT as sm4_ENCRYPT, DECRYPT as sm4_DECRYPT


class SMX:
    @staticmethod
    def generate_sm2_key():
        pk, sk = sm2_generate_keypair()
        return {"pk": pk, "sk": sk}

    @staticmethod
    def generate_sm2_sign(string: str, DA, k, len_para, Hexstr=0, encoding="utf-8"):
        return sm2_Sign(string, DA, k, len_para, Hexstr=Hexstr, encoding=encoding)

    @staticmethod
    def verify_sm2_sign(sign, string: str, PA, len_para, Hexstr=0, encoding="utf-8"):
        return sm2_Verify(sign, string, PA, len_para, Hexstr=Hexstr, encoding=encoding)

    @staticmethod
    def encrypt(string: str, **kwargs):
        encrypt_type = kwargs.get("encrypt_type")
        encryption_algorithm = ["SM2", "SM3", "SM4"]
        encrypt_string = ""
        if encrypt_type in ["SM2", "SM3", "SM4"]:
            if encrypt_type == "SM2":
                encrypt_string = sm2_Encrypt(string.encode(kwargs.get("encoding", "utf-8")), kwargs.get("pk"),
                                             kwargs.get("len_para"),
                                             kwargs.get("Hexstr", 0), kwargs.get("encoding", "utf-8"),
                                             kwargs.get("hash_algorithm", "sm3"))
            elif encrypt_type == "SM3":
                sm3 = SM3()
                sm3.update(string)
                encrypt_string = sm3.hexdigest()
            elif encrypt_type == "SM4":
                sm4 = Sm4()
                sm4.sm4_set_key(kwargs.get("key_data"), kwargs.get("mode"))
                encrypt_string = sm4.sm4_crypt_ecb()
        else:
            raise Exception(
                f"{encrypt_type} is unsupported SMX algorithm,supported algorithm have {encryption_algorithm}")
        return encrypt_string

    @staticmethod
    def decrypt(string: str, **kwargs):
        decrypt_type = kwargs.get("encrypt_type")
        decrypt_algorithm = ["SM2", "SM3", "SM4"]
        decrypt_string = ""
        if decrypt_type in ["SM2", "SM3", "SM4"]:
            if decrypt_type == "SM2":
                decrypt_string = sm2_Decrypt(string, kwargs.get("sk"), kwargs.get("len_para"), kwargs.get("Hexstr", 0),
                                             kwargs.get("encoding", "utf-8"), kwargs.get("hash_algorithm", "sm3"))
            elif decrypt_type == "SM4":
                sm4 = Sm4()
                sm4.sm4_set_key(kwargs.get("key_data"), kwargs.get("mode"))
                decrypt_string = sm4.sm4_crypt_ecb(string)

        else:
            raise Exception(f"{decrypt_type} is unsupported SMX algorithm,supported algorithm have {decrypt_algorithm}")
        return decrypt_string
