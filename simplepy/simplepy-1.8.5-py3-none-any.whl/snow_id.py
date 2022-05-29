from snowflake.client import get_guid


def get_snow_id() -> int:
    """
    TODO: 单列实现 类封装
    获取雪花ID
    单列模式  直接调用了包内的单列
    :return:
    """
    return get_guid()
