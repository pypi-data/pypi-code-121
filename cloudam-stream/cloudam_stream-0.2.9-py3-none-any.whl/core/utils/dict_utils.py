import json

params = {'name': '小王', 'source_file': 'aaa.txt'}

'''
根据姓名查询参数
'''


def get_param_by_name(name):
    return params[name]

'''
根据属性名查询属性值
'''
def get_property_value(object_desc, property_name, default=None):
    property_value = default
    if type(object_desc) == str:
        object_desc = json.loads(object_desc)
    if type(object_desc) == dict:
        property_value = object_desc.get(property_name, default)
    return property_value
