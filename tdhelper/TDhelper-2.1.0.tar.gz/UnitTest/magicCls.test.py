import __init__
import unittest
from TDhelper.MagicCls.model import model, createCls
from TDhelper.MagicCls.FieldsType import FieldType


class categories(model):
    category_id = FieldType(int, "type_id")
    category_name = FieldType(str, "type_name")

    def __init__(self, source, convert_type="json"):
        super(categories, self).__init__(source, convert_type)


class TestmagicCls(unittest.TestCase):
    def test_magicCls(self):
        api_json = [
            '{"type_id": 0, "type_name": "电影0"}',
            '[{"type_id": 1, "type_name": "电影1"},{"type_id": 2, "type_name": "电影2"},{"type_id": 3, "type_name": "电影3"}]',
            [
                {"type_id": 4, "type_name": "电影4"},
                {"type_id": 5, "type_name": "电影5"},
                {"type_id": 6, "type_name": "电影6"},
            ],
            {"type_id": 7, "type_name": "电影7"},
        ]
        for v in api_json:
            # create cls
            mapping = {"type_id": [int], "name": [str, "type_name"]}
            m_result = createCls("categories", mapping, v)
            self.assertRaises(Exception, m_result)
            print("\r\n-----------------create cls----------------------\r\n")
            for o in m_result.items():
                print(o.type_id)
                print(o.name)

            # mapping object.
            print("\r\n-----------------mapping object----------------------\r\n")
            m_result = categories(v)
            self.assertRaises(Exception, m_result)
            for o in m_result.items():
                print(o.category_id)
                print(o.category_name)


if __name__ == "__main__":
    unittest.main()
