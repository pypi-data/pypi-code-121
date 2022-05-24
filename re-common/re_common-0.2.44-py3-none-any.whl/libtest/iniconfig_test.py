def test_BaseAbs_config():
    """
    命令行下　在当前目录使用该命令测试
    pytest iniconfig_test.py::test_BaseAbs_config -s
    :return:
    """
    from re_common.baselibrary.baseabs import BaseAbs
    # get_conf_dict　参数
    # configfile 不传为前面配置好的路径　也可以给新的路径
    # encoding 指定编码
    # keep_keys_case 保持建大写，配置为Ｆａｓｌｅ会全部小写
    orderdicts = BaseAbs.get_config_factory().get_config_factory().ini_factory().set_config_path(
        "./config.ini").set_keep_keys_case(False).builder().get_config_dict()

    print(orderdicts)
    print(orderdicts["db"])
    print(orderdicts["db"]["psw"])


def test_Iniconfig_config():
    """
    第二种简便用法
    命令行下　在当前目录使用该命令测试
    pytest iniconfig_test.py::test_Iniconfig_config -s
    :return:
    """
    from re_common.baselibrary import IniConfig
    orderdicts = IniConfig("./config.ini").set_keep_keys_case(False).builder().get_config_dict()
    print(orderdicts)
    print(orderdicts["db"])
    print(orderdicts["Db2"]["psw"])

# 已经导如facade 可以通过　facade 直接导入
# from facade import IniConfig
# 建议外部使用导入时　全部通过facade 导入
