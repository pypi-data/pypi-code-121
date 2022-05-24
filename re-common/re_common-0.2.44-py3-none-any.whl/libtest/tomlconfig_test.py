
def test_BaseAbs_config():
    """
    命令行下　在当前目录使用该命令测试
    pytest tomlconfig_test.py::test_BaseAbs_config -s
    :return:
    """
    from re_common.baselibrary.baseabs import BaseAbs
    dicts = BaseAbs.get_config_factory().toml_factory().set_config_path(
        "./config_down.toml").read_file_remove_bom().get_dicts(encoding="utf-8")

    print(type(dicts))
    print(dicts)


def test_Tomlconfig_config():
    """
    第二种简便用法
    命令行下　在当前目录使用该命令测试
    pytest tomlconfig_test.py::test_Tomlconfig_config -s
    :return:
    """
    from re_common.baselibrary.readconfig.toml_config import TomlConfig
    dicts = TomlConfig("./config_down.toml").read_file_remove_bom().get_dicts()
    print(type(dicts))
    print(dicts)

# 已经导如facade 可以通过　facade 直接导入
# from facade import IniConfig
# 建议外部使用导入时　全部通过facade 导入
