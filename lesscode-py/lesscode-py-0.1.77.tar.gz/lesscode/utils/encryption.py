import importlib


class Algorithm:

    @staticmethod
    def get_one_way_encryption_algorithm_list():
        """
        单向加密算法
        :return:
        """
        one_way_encryption_algorithm_list = ["MD5", "SHA256", "SHA1", "HMAC"]
        return one_way_encryption_algorithm_list

    @staticmethod
    def get_symmetric_encryption_algorithm_list():
        """
        对称加密算法
        :return:
        """
        symmetric_encryption_algorithm_list = ["AES", "BASE64", "DES"]
        return symmetric_encryption_algorithm_list

    @staticmethod
    def get_asymmetric_encryption_algorithm_list():
        """
        非对称加密算法
        :return:
        """
        asymmetric_encryption_algorithm_list = ["RSA"]
        return asymmetric_encryption_algorithm_list

    @staticmethod
    def get_all_encryption_algorithm():
        one_way_encryption_algorithm_list = Algorithm.get_one_way_encryption_algorithm_list()
        symmetric_encryption_algorithm_list = Algorithm.get_symmetric_encryption_algorithm_list()
        asymmetric_encryption_algorithm_list = Algorithm.get_asymmetric_encryption_algorithm_list()
        algorithm_list = []
        algorithm_list.extend(one_way_encryption_algorithm_list)
        algorithm_list.extend(symmetric_encryption_algorithm_list)
        algorithm_list.extend(asymmetric_encryption_algorithm_list)
        return list(set(algorithm_list))

    @staticmethod
    def encrypt(string: str, algorithm: str, params: dict = {}):
        all_encryption_algorithm = Algorithm.get_all_encryption_algorithm()
        if algorithm in all_encryption_algorithm:
            algorithm_lib = importlib.import_module(f"lesscode.utils.encryption_algorithm")
            if params:
                return algorithm_lib.__getattribute__(algorithm).encrypt(string, **params)
            else:
                return algorithm_lib.__getattribute__(algorithm).encrypt(string)
        else:
            raise Exception(f"{algorithm} is unsupported algorithm,supported algorithm have {all_encryption_algorithm}")

    @staticmethod
    def decrypt(string: str, algorithm: str, params: dict = {}):
        symmetric_encryption_algorithm_list = Algorithm.get_symmetric_encryption_algorithm_list()
        asymmetric_encryption_algorithm_list = Algorithm.get_asymmetric_encryption_algorithm_list()
        encryption_algorithm_list = []
        encryption_algorithm_list.extend(symmetric_encryption_algorithm_list)
        encryption_algorithm_list.extend(asymmetric_encryption_algorithm_list)
        encryption_algorithm_list = list(set(encryption_algorithm_list))
        if algorithm in encryption_algorithm_list:
            algorithm_lib = importlib.import_module(f"lesscode.utils.encryption_algorithm")
            if params:
                return algorithm_lib.__getattribute__(algorithm).decrypt(string, **params)
            else:
                return algorithm_lib.__getattribute__(algorithm).decrypt(string, **params)
        else:
            raise Exception(
                f"{algorithm} is unsupported algorithm,supported algorithm have {encryption_algorithm_list}")
