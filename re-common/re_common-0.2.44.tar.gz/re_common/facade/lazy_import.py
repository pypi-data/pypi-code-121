# 延迟导入　主要是为了使用时不去安装多余的


def get_TomlConfig():
    from re_common.baselibrary.readconfig.toml_config import TomlConfig
    return TomlConfig


def get_streamlogger():
    from re_common.baselibrary import MLogger
    return MLogger().streamlogger
