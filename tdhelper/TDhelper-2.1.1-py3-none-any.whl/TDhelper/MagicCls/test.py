from model import model, createCls
from FieldsType import FieldType


class categories(model):
    category_id = FieldType(int, "type_id")
    category_name = FieldType(str, "type_name")

    def __init__(self, source, convert_type="json"):
        super(categories, self).__init__(source, convert_type)


if __name__ == "__main__":
    api_json = '[{"type_id": 1, "type_name": "电影"},{"type_id": 2, "type_name": "电影2"},{"type_id": 3, "type_name": "电影3"}]'#[{"type_id": 1, "type_name": "电影"},{"type_id": 2, "type_name": "电影2"},{"type_id": 3, "type_name": "电影3"}] #{"type_id": 1, "type_name": "电影"}#
    mapping = {"type_id": [int], "name": [str,"type_name"]}
    a = createCls("categories", mapping, api_json) #categories(api_json)
    for o in a.items():
        print(o.type_id)
        print(o.name)
        #print(o.category_id)
        #print(o.category_name)
