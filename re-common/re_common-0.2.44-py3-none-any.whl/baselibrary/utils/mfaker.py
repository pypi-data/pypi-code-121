import random

from faker import Faker


# https://www.jianshu.com/p/20e41fc65dc8

class MFaker(Faker):
    # 生成名字
    m_name = "name"
    # 生成地址
    m_address = "address"
    # 生成国家
    m_country = "country"
    # 生成省份
    m_province = "province"
    # 生成市　县
    m_city_suffix = "city_suffix"

    # 以下结构都可以用　py_para　结构的参数
    # 生成dict
    m_pydict = "pydict"
    # 生成list
    m_pylist = "pylist"
    # 生成iterable
    m_pyiterable = "pyiterable"
    # 生成set
    m_pyset = "pyset"
    # 生成tuple
    m_pytuple = "pytuple"

    def create_data(self, types, **kwargs):
        """
        :param types: 是上面的类型
        :param kwargs: 类型的参数
        :return:
        """
        if kwargs:
            print(kwargs)
            return getattr(self, types)(**kwargs)
        return getattr(self, types)()

    def py_para(self, num=10):
        """
        python 集合参数　适用于python 原生集合
        pydict pylist 的参数
        :return:
        """
        return {"nb_elements": num, "variable_nb_elements": True}

    def get_page(self):
        return random.randint(1, 150)





